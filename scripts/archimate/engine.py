"""Headless ArchiMate 3.2 Open Exchange model operations.

Standard-library-only engine providing side-effect-free reads/queries,
structured transactional mutations, two-tier validation, deterministic
NCName identifiers, preservation-or-fail-closed round-tripping, and atomic
persistence with a single-writer gate.
"""
from __future__ import annotations

import argparse
import copy
import fcntl
import hashlib
import json
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

ARCHIMATE_NS = "http://www.opengroup.org/xsd/archimate/3.0/"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"

NCNAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\-]*$")
_NS_DECL = re.compile(rb'\sxmlns:([A-Za-z0-9_.\-]+)="([^"]*)"')
_DEFAULT_NS_DECL = re.compile(rb'\sxmlns="([^"]*)"')
_SERVICE_TYPES = ("Service",)
_ACTOR_TYPES = ("Actor", "Role", "Collaboration", "Interface")


class ModelError(ValueError):
    """A fail-closed model, mutation, or persistence error."""


@dataclass(frozen=True)
class ValidationIssue:
    """One structural or semantic violation with stable rule identifiers."""

    rule: str
    construct: str
    message: str
    endpoint_ids: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "construct": self.construct,
            "message": self.message,
            "endpoint_ids": list(self.endpoint_ids),
        }


def deterministic_id(kind: str, element_type: str, name: str) -> str:
    """Return the normative per-kind deterministic ArchiMate NCName."""
    prefixes = {"model": "model", "element": "ea", "relationship": "rel", "view": "view", "organization_item": "item", "property_definition": "prop", "diagram_node": "node", "diagram_connection": "conn"}
    if kind not in prefixes:
        raise ModelError(f"IDENTITY_UNKNOWN_KIND: {kind}")
    identity = f"archimate:3.2|{kind}|{element_type.strip()}|{name.strip()}"
    return f"{prefixes[kind]}-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:16]}"


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _attr(node: ET.Element, *names: str) -> str | None:
    for key, value in node.attrib.items():
        if key in names or _local(key) in names:
            return value
    return None


def _find_all(root: ET.Element, local_name: str) -> list[ET.Element]:
    return [node for node in root.iter() if _local(node.tag) == local_name]


def _element_type(node: ET.Element) -> str:
    value = _attr(node, "type") or ""
    return value.split(":")[-1]


def _element_layer(element_type: str) -> str:
    for prefix in ("Business", "Application", "Technology", "Physical",
                   "Implementation", "Motivation", "Strategy"):
        if element_type.startswith(prefix):
            return prefix.lower()
    return "other"


def _child_text(node: ET.Element, local_name: str) -> str:
    for child in node:
        if _local(child.tag) == local_name and child.text is not None:
            return child.text
    return ""


def _set_child_text(node: ET.Element, local_name: str, text: str) -> None:
    for child in node:
        if _local(child.tag) == local_name:
            child.text = text
            return
    child = ET.SubElement(node, local_name)
    child.text = text


def _container(root: ET.Element, local_name: str) -> ET.Element:
    for child in root:
        if _local(child.tag) == local_name:
            return child
    return ET.SubElement(root, local_name)


def _register_namespaces(raw: bytes) -> str | None:
    """Register declared namespace prefixes so serialization preserves them."""
    for match in _NS_DECL.finditer(raw):
        prefix = match.group(1).decode("ascii")
        if prefix != "xml" and not prefix.startswith("ns"):
            ET.register_namespace(prefix, match.group(2).decode("utf-8"))
    ET.register_namespace("xsi", XSI_NS)
    default = _DEFAULT_NS_DECL.search(raw)
    if default is None:
        return None
    return default.group(1).decode("utf-8")


class ArchimateModel:
    """Read/query and structured mutation facade for one exchange XML file."""

    def __init__(self, path: Path, root: ET.Element, raw: bytes, default_ns: str | None):
        self.path = Path(path)
        self.root = root
        self.raw = raw
        self.default_ns = default_ns
        self._elements = {
            str(_attr(node, "identifier")): node
            for node in _find_all(root, "element")
            if _attr(node, "identifier")
        }
        self._relationships = {
            str(_attr(node, "identifier")): node
            for node in _find_all(root, "relationship")
            if _attr(node, "identifier")
        }

    # ------------------------------------------------------------------ load

    @classmethod
    def load(cls, path: str | Path) -> ArchimateModel:
        target = Path(path)
        raw = target.read_bytes()
        default_ns = _register_namespaces(raw)
        parser = ET.XMLParser(
            target=ET.TreeBuilder(insert_comments=True, insert_pis=True)
        )
        try:
            root = ET.fromstring(raw, parser=parser)
        except ET.ParseError as exc:
            raise ModelError(f"STRUCTURE_XML_NOT_WELL_FORMED: {exc}") from exc
        return cls(target, root, raw, default_ns)

    # ----------------------------------------------------------------- reads

    def metadata(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "model_identifier": _attr(self.root, "identifier") or "",
            "root": _local(self.root.tag),
            "elements": len(self._elements),
            "relationships": len(self._relationships),
            "views": len(_find_all(self.root, "view")),
            "namespaces": sorted(
                {
                    node.tag[1:].split("}", 1)[0]
                    for node in self.root.iter()
                    if node.tag.startswith("{")
                }
            ),
        }

    def elements(
        self,
        *,
        layer: str | None = None,
        type: str | None = None,
        name: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, str]]:
        if limit < 0:
            raise ModelError("QUERY_INVALID_LIMIT")
        pattern = re.compile(name) if name else None
        result: list[dict[str, str]] = []
        for identifier, node in sorted(self._elements.items()):
            node_type = _element_type(node)
            node_layer = _element_layer(node_type)
            node_name = node.get("name") or _child_text(node, "name")
            if layer and node_layer != layer.lower():
                continue
            if type and node_type != type:
                continue
            if pattern is not None and not pattern.search(node_name):
                continue
            result.append(
                {"identifier": identifier, "type": node_type, "name": node_name}
            )
            if len(result) >= limit:
                break
        return result

    def relationships(
        self,
        *,
        type: str | None = None,
        source: str | None = None,
        target: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, str]]:
        if limit < 0:
            raise ModelError("QUERY_INVALID_LIMIT")
        result: list[dict[str, str]] = []
        for identifier, node in sorted(self._relationships.items()):
            node_type = _element_type(node)
            src = _attr(node, "source") or ""
            dst = _attr(node, "target") or ""
            if type and node_type != type:
                continue
            if source and src != source:
                continue
            if target and dst != target:
                continue
            result.append(
                {"identifier": identifier, "type": node_type, "source": src, "target": dst}
            )
            if len(result) >= limit:
                break
        return result

    def neighbors(self, identifier: str, *, depth: int = 1, limit: int = 100) -> dict[str, Any]:
        """Bounded neighborhood traversal around one element."""
        if identifier not in self._elements:
            raise ModelError(f"QUERY_UNKNOWN_ELEMENT: {identifier}")
        if depth < 0 or limit < 0:
            raise ModelError("QUERY_INVALID_BOUNDS")
        adjacency: dict[str, list[dict[str, str]]] = {}
        for rel in self.relationships(limit=len(self._relationships) or 1):
            adjacency.setdefault(rel["source"], []).append(rel)
            adjacency.setdefault(rel["target"], []).append(rel)
        seen = {identifier}
        frontier = {identifier}
        edges: list[dict[str, str]] = []
        for _ in range(depth):
            next_frontier: set[str] = set()
            for member in sorted(frontier):
                for rel in adjacency.get(member, []):
                    if rel not in edges:
                        edges.append(rel)
                    other = rel["target"] if rel["source"] == member else rel["source"]
                    if other not in seen:
                        seen.add(other)
                        next_frontier.add(other)
            frontier = next_frontier
            if not frontier:
                break
        truncated = len(edges) > limit or len(seen) > limit
        members = [
            element
            for element in self.elements(limit=len(self._elements) or 1)
            if element["identifier"] in seen
        ]
        return {
            "root": identifier,
            "depth": depth,
            "elements": members[:limit],
            "relationships": sorted(edges[:limit], key=lambda rel: rel["identifier"]),
            "truncated": truncated,
        }

    def views(self) -> list[dict[str, Any]]:
        listing: list[dict[str, Any]] = []
        for node in _find_all(self.root, "view"):
            listing.append(
                {
                    "identifier": _attr(node, "identifier") or "",
                    "name": _child_text(node, "name"),
                    "nodes": len(_find_all(node, "node")),
                    "connections": len(_find_all(node, "connection")),
                }
            )
        return listing

    def organizations(self) -> list[dict[str, Any]]:
        listing: list[dict[str, Any]] = []
        # Open Exchange uses organizations/item trees rather than an
        # ``organization`` element. Report the top-level item trees.
        for container in _find_all(self.root, "organizations"):
            for node in _find_all(container, "item"):
                label = _child_text(node, "label")
                if not label:
                    continue
                listing.append(
                    {
                        "identifier": _attr(node, "identifier") or "",
                        "label": label,
                        "items": len(_find_all(node, "item")),
                    }
                )
        return listing

    # ------------------------------------------------------------ validation

    def validate(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        issues.extend(self._structural_issues())
        issues.extend(self._semantic_issues())
        return issues

    def _structural_issues(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        identifiers: set[str] = set()
        for node in self.root.iter():
            identifier = _attr(node, "identifier") or _attr(node, "id")
            if identifier:
                if identifier in identifiers:
                    issues.append(
                        ValidationIssue(
                            "STRUCTURAL_DUPLICATE_IDENTIFIER",
                            identifier,
                            "duplicate identifier in model",
                        )
                    )
                else:
                    identifiers.add(identifier)
                if not NCNAME.fullmatch(identifier):
                    issues.append(
                        ValidationIssue(
                            "STRUCTURAL_INVALID_IDENTIFIER",
                            identifier,
                            "identifier is not a valid NCName",
                        )
                    )
        known = set(self._elements) | set(self._relationships)
        identifier_refs = known | {
            _attr(node, "identifier") or ""
            for node in _find_all(self.root, "view")
        } - {""}
        known_by_ref = {
            "elementRef": known,
            "relationshipRef": known,
            "identifierRef": identifier_refs,
        }
        for rel_id, rel in sorted(self._relationships.items()):
            src = _attr(rel, "source") or ""
            dst = _attr(rel, "target") or ""
            missing = [endpoint for endpoint in (src, dst) if endpoint not in self._elements]
            if missing:
                issues.append(
                    ValidationIssue(
                        "STRUCTURAL_IDREF_UNRESOLVED",
                        rel_id,
                        "relationship endpoint does not resolve to an element",
                        tuple(missing),
                    )
                )
        for node in self.root.iter():
            for attr_name, ref in node.attrib.items():
                local_name = _local(attr_name)
                if local_name not in ("elementRef", "relationshipRef", "identifierRef"):
                    continue
                if ref not in known_by_ref[local_name]:
                    issues.append(
                        ValidationIssue(
                            "STRUCTURAL_IDREF_UNRESOLVED",
                            ref,
                            f"{local_name} does not resolve",
                            (ref,),
                        )
                    )
            ref = _attr(node, "ref") or _attr(node, "identifierRef")
            if ref is not None and _local(node.tag) in ("elementRef", "relationshipRef"):
                ref_kind = _local(node.tag)
                if ref not in known_by_ref[ref_kind]:
                    issues.append(
                        ValidationIssue(
                            "STRUCTURAL_IDREF_UNRESOLVED", ref, f"{_local(node.tag)} does not resolve", (ref,)
                        )
                    )
        return issues

    def _semantic_issues(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for rel_id, rel in sorted(self._relationships.items()):
            src = _attr(rel, "source") or ""
            dst = _attr(rel, "target") or ""
            src_node = self._elements.get(src)
            dst_node = self._elements.get(dst)
            if src_node is None or dst_node is None:
                continue
            rel_type = _element_type(rel)
            src_type = _element_type(src_node)
            dst_type = _element_type(dst_node)
            if rel_type == "Serving":
                # Serving runs provider -> consumer: the provider endpoint is
                # a service; a service appearing as the target means the
                # relationship direction was inverted.
                src_is_service = src_type.endswith(_SERVICE_TYPES)
                dst_is_service = dst_type.endswith(_SERVICE_TYPES)
                if dst_is_service and not src_is_service:
                    issues.append(
                        ValidationIssue(
                            "SEMANTIC_SERVING_REVERSED",
                            rel_id,
                            "Serving must run provider (source) to consumer "
                            "(target); a service element as target indicates "
                            "inverted direction",
                            (src, dst),
                        )
                    )
            if rel_type in ("Composition", "Aggregation"):
                # Active-structure actors cannot compose behavioral service
                # elements.
                if src_type.endswith(_ACTOR_TYPES) and dst_type.endswith(_SERVICE_TYPES):
                    issues.append(
                        ValidationIssue(
                            "SEMANTIC_ILLEGAL_ENDPOINT_PAIR",
                            rel_id,
                            f"{rel_type} from {src_type} to {dst_type} is not "
                            "a legal element/relationship pairing",
                            (src, dst),
                        )
                    )
        return issues

    # ------------------------------------------------------------- mutation

    def mutate(self, operations: Sequence[Mapping[str, Any]], *, backup: bool = True) -> None:
        """Apply a batch of structured operations transactionally.

        Either every operation in the batch validates and persists, or the
        model file stays byte-identical to its pre-batch state.
        """
        self._preservation_gate()
        candidate_root = copy.deepcopy(self.root)
        trial = ArchimateModel(self.path, candidate_root, self.raw, self.default_ns)
        for operation in operations:
            trial._apply(operation)
        issues = trial.validate()
        if issues:
            raise ModelError(
                "MUTATION_REJECTED: "
                + json.dumps([issue.as_dict() for issue in issues], sort_keys=True)
            )
        payload = trial._serialize(candidate_root)
        self._persist(payload, backup=backup)
        self.root = candidate_root
        self.raw = payload
        self._elements = trial._elements
        self._relationships = trial._relationships

    def _preservation_gate(self) -> None:
        """Refuse mutations the serializer cannot round-trip safely."""
        if b"<!DOCTYPE" in self.raw:
            raise ModelError("PRESERVATION_FAIL_CLOSED: DOCTYPE declarations are not preserved")
        if b"<![CDATA[" in self.raw:
            raise ModelError("PRESERVATION_FAIL_CLOSED: CDATA sections are not preserved")
        baseline = ET.tostring(self.root, encoding="utf-8", xml_declaration=True)
        raw_comments = self.raw.count(b"<!--")
        baseline_comments = baseline.count(b"<!--")
        raw_pis = len(re.findall(rb"<\?", self.raw))
        baseline_pis = len(re.findall(rb"<\?", baseline))
        if raw_comments != baseline_comments or raw_pis != baseline_pis:
            raise ModelError("PRESERVATION_FAIL_CLOSED: constructs would not survive round-trip")

    def _serialize(self, root: ET.Element) -> bytes:
        """Serialize the tree, restoring the default-namespace form when the
        fallback path renames the original default namespace to an nsN prefix."""
        kwargs: dict[str, Any] = {"encoding": "utf-8", "xml_declaration": True}
        if self.default_ns:
            try:
                kwargs["default_namespace"] = self.default_ns
                return ET.tostring(root, **kwargs)
            except ValueError as exc:
                if "non-qualified names" not in str(exc):
                    raise ModelError(f"PRESERVATION_FAIL_CLOSED: {exc}") from exc
                kwargs.pop("default_namespace", None)
        payload = ET.tostring(root, **kwargs)
        if self.default_ns:
            prefix_decl = re.search(
                rb'xmlns:(ns\d+)="' + re.escape(self.default_ns.encode("utf-8")) + rb'"',
                payload,
            )
            if prefix_decl:
                prefix = prefix_decl.group(1)
                open_tag = b"<" + prefix + b":"
                close_tag = b"</" + prefix + b":"
                if open_tag in payload or close_tag in payload:
                    payload = payload.replace(close_tag, b"</")
                    payload = payload.replace(open_tag, b"<")
                    payload = payload.replace(
                        prefix_decl.group(0), b'xmlns="' + self.default_ns.encode("utf-8") + b'"'
                    )
        return payload
    
    def _apply(self, op: Mapping[str, Any]) -> None:
        action = op.get("op")
        if action == "create_element":
            element_type = str(op.get("type", ""))
            name = str(op.get("name", ""))
            layer = str(op.get("layer", ""))
            if not element_type or not name:
                raise ModelError("MUTATION_INVALID_ELEMENT: type and name are required")
            identifier = str(
                op.get("identifier") or deterministic_id("element", element_type, name)
            )
            if identifier in self._elements:
                return  # idempotent re-application
            if not NCNAME.fullmatch(identifier):
                raise ModelError(f"MUTATION_INVALID_ID: {identifier}")
            container = _container(self.root, "elements")
            node = ET.SubElement(
                container,
                f"{{{self.default_ns}}}element" if self.default_ns else "element",
                {"identifier": identifier},
            )
            node.set(f"{{{XSI_NS}}}type", element_type)
            name_child = ET.SubElement(
                node, f"{{{self.default_ns}}}name" if self.default_ns else "name"
            )
            name_child.text = name
            self._elements[identifier] = node
        elif action == "update_element":
            identifier = str(op.get("identifier", ""))
            node = self._elements.get(identifier)
            if node is None:
                raise ModelError(f"MUTATION_UNKNOWN_ELEMENT: {identifier}")
            if "name" in op:
                if "name" in node.attrib:
                    node.set("name", str(op["name"]))
                else:
                    _set_child_text(node, "name", str(op["name"]))
            if "documentation" in op:
                _set_child_text(node, "documentation", str(op["documentation"]))
        elif action == "delete_element":
            identifier = str(op.get("identifier", ""))
            node = self._elements.get(identifier)
            if node is None:
                raise ModelError(f"MUTATION_UNKNOWN_ELEMENT: {identifier}")
            referenced_by = self._element_reference_holders(identifier)
            if referenced_by:
                raise ModelError(
                    f"MUTATION_REFERENCED_ELEMENT: {identifier} is referenced by "
                    + ", ".join(referenced_by)
                )
            self._remove(node)
            del self._elements[identifier]
        elif action == "create_relationship":
            rel_type = str(op.get("type", ""))
            source = str(op.get("source", ""))
            target = str(op.get("target", ""))
            if not rel_type or source not in self._elements or target not in self._elements:
                raise ModelError("MUTATION_INVALID_RELATIONSHIP: type and resolvable endpoints required")
            identifier = str(
                op.get("identifier")
                or deterministic_id("relationship", rel_type, f"{source}->{target}")
            )
            if identifier in self._relationships:
                return  # idempotent re-application
            if not NCNAME.fullmatch(identifier):
                raise ModelError(f"MUTATION_INVALID_ID: {identifier}")
            container = _container(self.root, "relationships")
            node = ET.SubElement(
                container,
                f"{{{self.default_ns}}}relationship" if self.default_ns else "relationship",
                {"identifier": identifier, "source": source, "target": target},
            )
            node.set(f"{{{XSI_NS}}}type", rel_type)
            self._relationships[identifier] = node
        elif action == "delete_relationship":
            identifier = str(op.get("identifier", ""))
            node = self._relationships.get(identifier)
            if node is None:
                raise ModelError(f"MUTATION_UNKNOWN_RELATIONSHIP: {identifier}")
            if self._relationship_reference_holders(identifier):
                raise ModelError(
                    f"MUTATION_REFERENCED_RELATIONSHIP: {identifier} is referenced by a view connection"
                )
            self._remove(node)
            del self._relationships[identifier]
        else:
            raise ModelError(f"MUTATION_UNSUPPORTED_OPERATION: {action!r}")

    def _remove(self, node: ET.Element) -> None:
        parent = self._find_parent(node)
        if parent is not None:
            parent.remove(node)

    def _find_parent(self, target: ET.Element) -> ET.Element | None:
        for node in self.root.iter():
            if target in list(node):
                return node
        return None

    def _element_reference_holders(self, identifier: str) -> list[str]:
        holders: list[str] = []
        for rel in self._relationships.values():
            if (_attr(rel, "source") or "") == identifier or (_attr(rel, "target") or "") == identifier:
                holders.append(f"relationship:{_attr(rel, 'identifier')}")
        for node in self.root.iter():
            ref = _attr(node, "ref") or _attr(node, "elementRef") or _attr(node, "identifierRef")
            if ref == identifier:
                view = self._nearest_ancestor_identifier(node)
                holders.append(view)
        return holders

    def _relationship_reference_holders(self, identifier: str) -> list[str]:
        holders: list[str] = []
        for node in self.root.iter():
            ref = _attr(node, "ref") or _attr(node, "relationshipRef")
            if ref == identifier:
                holders.append(self._nearest_ancestor_identifier(node))
        return holders

    def _nearest_ancestor_identifier(self, node: ET.Element) -> str:
        current: ET.Element | None = self._find_parent(node)
        while current is not None:
            identifier = _attr(current, "identifier")
            if identifier:
                return identifier
            current = self._find_parent(current)
        return "unknown-holder"

    # ----------------------------------------------------------- persistence

    def _persist(self, payload: bytes, *, backup: bool) -> None:
        path = self.path.resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        lock_path = path.parent / f".{path.name}.lock"
        with open(lock_path, "a+b") as lock_handle:
            try:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise ModelError("PERSISTENCE_SINGLE_WRITER_BUSY: another writer holds the model lock") from exc
            try:
                if backup:
                    backup_path = path.parent / f"{path.name}.bak"
                    backup_path.write_bytes(self.raw)
                descriptor, temporary_name = tempfile.mkstemp(
                    prefix=f".{path.name}.", dir=path.parent
                )
                try:
                    with os.fdopen(descriptor, "wb") as stream:
                        stream.write(payload)
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.chmod(temporary_name, path.stat().st_mode & 0o777)
                    os.replace(temporary_name, path)
                    directory = os.open(path.parent, os.O_RDONLY)
                    try:
                        os.fsync(directory)
                    finally:
                        os.close(directory)
                finally:
                    if os.path.exists(temporary_name):
                        os.unlink(temporary_name)
            finally:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


# ----------------------------------------------------------------------- CLI


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="archimate",
        description="Headless ArchiMate 3.2 Open Exchange model operations",
    )
    parser.add_argument("--model", type=Path, required=True, help="path to exchange XML model")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("inspect", help="model metadata")
    subparsers.add_parser("validate", help="structural + semantic validation")
    subparsers.add_parser("views", help="list views and organizations")

    query = subparsers.add_parser("query", help="filtered element query")
    query.add_argument("--layer")
    query.add_argument("--type")
    query.add_argument("--name")
    query.add_argument("--limit", type=int, default=100)

    rel_query = subparsers.add_parser("query-relationships", help="filtered relationship query")
    rel_query.add_argument("--type")
    rel_query.add_argument("--source")
    rel_query.add_argument("--target")
    rel_query.add_argument("--limit", type=int, default=100)

    neighbors = subparsers.add_parser("neighbors", help="bounded neighborhood traversal")
    neighbors.add_argument("--element", required=True)
    neighbors.add_argument("--depth", type=int, default=1)
    neighbors.add_argument("--limit", type=int, default=100)

    mutate = subparsers.add_parser("mutate", help="apply a structured operation batch atomically")
    mutate.add_argument("operations", type=Path, help="JSON file with the operation list")
    mutate.add_argument("--no-backup", action="store_true", help="skip the pre-mutation backup")

    args = parser.parse_args(argv)
    try:
        model = ArchimateModel.load(args.model)
        if args.command == "inspect":
            output: dict[str, Any] = model.metadata()
        elif args.command == "validate":
            issues = [issue.as_dict() for issue in model.validate()]
            output = {"valid": not issues, "issues": issues}
            if issues:
                print(json.dumps(output, indent=2, sort_keys=True))
                return 3
        elif args.command == "views":
            output = {"views": model.views(), "organizations": model.organizations()}
        elif args.command == "query":
            output = {
                "elements": model.elements(
                    layer=args.layer, type=args.type, name=args.name, limit=args.limit
                )
            }
        elif args.command == "query-relationships":
            output = {
                "relationships": model.relationships(
                    type=args.type, source=args.source, target=args.target, limit=args.limit
                )
            }
        elif args.command == "neighbors":
            output = model.neighbors(args.element, depth=args.depth, limit=args.limit)
        else:
            operations = json.loads(args.operations.read_text(encoding="utf-8"))
            if not isinstance(operations, list):
                raise ModelError("MUTATION_INVALID_BATCH: operations must be a JSON array")
            model.mutate(operations, backup=not args.no_backup)
            output = model.metadata()
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except ModelError as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 4
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
