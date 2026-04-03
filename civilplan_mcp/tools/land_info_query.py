from __future__ import annotations

import csv
from html import unescape
from io import TextIOWrapper
import json
import re
from typing import Any, Iterable
from xml.etree import ElementTree as ET
import zipfile

import httpx

from civilplan_mcp.config import get_settings
from civilplan_mcp.models import ProjectDomain
from civilplan_mcp.tools._base import wrap_response


VWORLD_ADDRESS_URL = "https://api.vworld.kr/req/address"
VWORLD_DATA_URL = "https://api.vworld.kr/req/data"
VWORLD_WFS_URL = "https://api.vworld.kr/req/wfs"
EUM_LAND_USE_URL = "https://www.eum.go.kr/eum/plan/info/getLandUseInfo"
EUM_LAND_USE_GY_AJAX_URL = "https://www.eum.go.kr/web/ar/lu/luLandDetUseGYAjax.jsp"
CADASTRAL_LAYER = "LP_PA_CBND_BUBUN"
LAND_USE_LAYER = "LT_C_LHBLPN"
LAND_PRICE_DIR = "land_prices"

_LAND_USE_ALIASES = {
    "use_district": (
        "usedistrict",
        "usedistrictnm",
        "usedistrictname",
        "usedistrictnm1",
        "useDistrict",
        "zonenm",
        "zonename",
        "landuse",
    ),
    "district_2": (
        "district2",
        "usedistrict2",
        "usedistrict2nm",
        "usedistrict2name",
        "usezone",
        "usezonename",
    ),
    "bcr": ("bcr", "bcrrate", "buildingcoverage"),
    "far": ("far", "farrate", "floorarearatio"),
    "height_limit_m": ("height", "heightlimit", "heightlimitm"),
}
_LAND_PRICE_KEY_ALIASES = {"pnu", "필지고유번호", "법정동코드"}
_LAND_PRICE_VALUE_ALIASES = {"공시지가", "landprice", "지가"}


def extract_address_result(payload: dict[str, Any]) -> dict[str, Any]:
    response = payload.get("response", {})
    if response.get("status") != "OK":
        error = response.get("error", {})
        raise ValueError(error.get("text", "address lookup failed"))

    result = response.get("result", {})
    point = result.get("point", {}) or {}
    items = result.get("items", []) or []
    first = items[0] if items else {}
    parcel = first.get("address", {}).get("parcel")
    pnu = first.get("id") or first.get("pnu")
    return {
        "pnu": pnu,
        "parcel_address": parcel,
        "x": float(point["x"]) if point.get("x") else None,
        "y": float(point["y"]) if point.get("y") else None,
    }


def extract_feature_properties(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("type") == "FeatureCollection":
        features = payload.get("features", [])
        if not features:
            return {}
        return features[0].get("properties", {}) or {}

    response = payload.get("response", {})
    if response.get("status") != "OK":
        error = response.get("error", {})
        raise ValueError(error.get("text", "feature lookup failed"))

    features = response.get("result", {}).get("featureCollection", {}).get("features", [])
    if not features:
        return {}
    return features[0].get("properties", {}) or {}


def build_land_use_bbox_params(x: float, y: float, api_key: str, buffer_deg: float = 0.0005) -> dict[str, Any]:
    return {
        "SERVICE": "WFS",
        "VERSION": "2.0.0",
        "REQUEST": "GetFeature",
        "TYPENAME": "lt_c_lhblpn",
        "BBOX": f"{x-buffer_deg:.4f},{y-buffer_deg:.4f},{x+buffer_deg:.4f},{y+buffer_deg:.4f},EPSG:4326",
        "SRSNAME": "EPSG:4326",
        "KEY": api_key,
        "OUTPUTFORMAT": "application/json",
    }


def _normalize_header(value: str) -> str:
    return re.sub(r"[^0-9a-z가-힣]+", "", value.lower())


def _open_tabular_text(binary_handle, suffix: str) -> Iterable[dict[str, Any]]:
    for encoding in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            wrapper = TextIOWrapper(binary_handle, encoding=encoding, newline="")
            sample = wrapper.read(2048)
            wrapper.seek(0)
            dialect = csv.excel_tab if suffix == ".tsv" else csv.Sniffer().sniff(sample or "a,b\n1,2\n")
            reader = csv.DictReader(wrapper, dialect=dialect)
            for row in reader:
                yield row
            return
        except UnicodeDecodeError:
            binary_handle.seek(0)
            continue
        except csv.Error:
            binary_handle.seek(0)
            wrapper = TextIOWrapper(binary_handle, encoding=encoding, newline="")
            reader = csv.DictReader(wrapper)
            for row in reader:
                yield row
            return


def _iter_land_price_rows(directory) -> Iterable[tuple[str, dict[str, Any]]]:
    for path in sorted(directory.glob("*")):
        suffix = path.suffix.lower()
        if suffix in {".csv", ".tsv"}:
            with path.open("rb") as handle:
                for row in _open_tabular_text(handle, suffix):
                    yield path.name, row
            continue

        if suffix != ".zip":
            continue

        with zipfile.ZipFile(path) as archive:
            for member_name in archive.namelist():
                member_suffix = member_name.lower().rsplit(".", 1)[-1] if "." in member_name else ""
                if member_suffix not in {"csv", "tsv"}:
                    continue
                with archive.open(member_name) as handle:
                    for row in _open_tabular_text(handle, f".{member_suffix}"):
                        yield f"{path.name}:{member_name}", row


def _read_land_price_from_files(pnu: str | None) -> dict[str, Any] | None:
    if not pnu:
        return None

    settings = get_settings()
    directory = settings.data_dir / LAND_PRICE_DIR
    if not directory.exists():
        return None

    key_aliases = {_normalize_header(alias) for alias in _LAND_PRICE_KEY_ALIASES}
    value_aliases = {_normalize_header(alias) for alias in _LAND_PRICE_VALUE_ALIASES}

    for source_name, row in _iter_land_price_rows(directory):
        normalized = {
            _normalize_header(str(key)): value for key, value in row.items() if key
        }
        row_pnu = next((value for key, value in normalized.items() if key in key_aliases), None)
        if str(row_pnu).strip() != pnu:
            continue

        price = next((value for key, value in normalized.items() if key in value_aliases), None)
        if not price:
            continue

        return {
            "individual_m2_won": int(float(str(price).replace(",", ""))),
            "source": source_name,
        }
    return None


def _fetch_address_to_pnu(address: str, api_key: str) -> dict[str, Any]:
    params = {
        "service": "address",
        "request": "getcoord",
        "version": "2.0",
        "crs": "epsg:4326",
        "refine": "true",
        "simple": "false",
        "format": "json",
        "type": "PARCEL",
        "address": address,
        "key": api_key,
    }
    response = httpx.get(VWORLD_ADDRESS_URL, params=params, timeout=20)
    response.raise_for_status()
    return extract_address_result(response.json())


def _fetch_vworld_properties(layer: str, pnu: str, api_key: str) -> dict[str, Any]:
    params = {
        "service": "data",
        "version": "2.0",
        "request": "GetFeature",
        "format": "json",
        "errorformat": "json",
        "data": layer,
        "attrFilter": f"pnu:=:{pnu}",
        "geometry": "false",
        "size": 1,
        "page": 1,
        "key": api_key,
    }
    response = httpx.get(VWORLD_DATA_URL, params=params, timeout=20)
    response.raise_for_status()
    return extract_feature_properties(response.json())


def _flatten_scalar_values(value: Any, bucket: dict[str, str]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            _flatten_scalar_values(nested, bucket)
            if not isinstance(nested, (dict, list)) and nested not in (None, ""):
                bucket[str(key).lower()] = str(nested)
        return

    if isinstance(value, list):
        for nested in value:
            _flatten_scalar_values(nested, bucket)


def _flatten_xml_values(text: str) -> dict[str, str]:
    root = ET.fromstring(text)
    bucket: dict[str, str] = {}
    for element in root.iter():
        tag = element.tag.split("}")[-1].lower()
        value = (element.text or "").strip()
        if value:
            bucket[tag] = value
    return bucket


def _pick_first(flattened: dict[str, str], aliases: tuple[str, ...]) -> str | None:
    for alias in aliases:
        if alias.lower() in flattened:
            return flattened[alias.lower()]
    return None


def _strip_tags(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(cleaned)).strip()


def extract_land_use_html_properties(html_text: str) -> dict[str, Any]:
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html_text, flags=re.IGNORECASE | re.DOTALL)
    data_rows: list[list[str]] = []
    for row_html in rows:
        columns = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row_html, flags=re.IGNORECASE | re.DOTALL)
        texts = [_strip_tags(column) for column in columns]
        if len(texts) != 3:
            continue
        if not texts[0] or "조회된 데이터가 없습니다" in texts[0]:
            continue
        if not re.search(r"\d", texts[1]) or not re.search(r"\d", texts[2]):
            continue
        data_rows.append(texts)

    result: dict[str, Any] = {}
    if data_rows:
        result["usedistrictnm"] = data_rows[0][0]
        result["bcr"] = re.search(r"\d+(?:\.\d+)?", data_rows[0][1]).group(0) if re.search(r"\d+(?:\.\d+)?", data_rows[0][1]) else None
        result["far"] = re.search(r"\d+(?:\.\d+)?", data_rows[0][2]).group(0) if re.search(r"\d+(?:\.\d+)?", data_rows[0][2]) else None
        if len(data_rows) > 1:
            result["usedistrict2nm"] = data_rows[1][0]

    popup_g = re.search(r'id="PopupG_pop[^"]*"[^>]*>(.*?)</td>', html_text, flags=re.IGNORECASE | re.DOTALL)
    popup_y = re.search(r'id="PopupY_pop[^"]*"[^>]*>(.*?)</td>', html_text, flags=re.IGNORECASE | re.DOTALL)
    if "bcr" not in result and popup_g:
        match = re.search(r"\d+(?:\.\d+)?", _strip_tags(popup_g.group(1)))
        if match:
            result["bcr"] = match.group(0)
    if "far" not in result and popup_y:
        match = re.search(r"\d+(?:\.\d+)?", _strip_tags(popup_y.group(1)))
        if match:
            result["far"] = match.group(0)

    return result


def extract_land_use_properties(response: httpx.Response) -> dict[str, Any]:
    flattened: dict[str, str] = {}
    body = response.text.strip()
    content_type = (response.headers.get("content-type") or "").lower()
    if not body:
        return {}

    if "json" in content_type:
        _flatten_scalar_values(response.json(), flattened)
    else:
        try:
            _flatten_scalar_values(response.json(), flattened)
        except (json.JSONDecodeError, ValueError):
            if body.startswith("<") and ("<html" in body.lower() or "<div" in body.lower()):
                return extract_land_use_html_properties(body)
            if body.startswith("<"):
                flattened = _flatten_xml_values(body)
            else:
                return {}

    return {
        "usedistrictnm": _pick_first(flattened, _LAND_USE_ALIASES["use_district"]),
        "usedistrict2nm": _pick_first(flattened, _LAND_USE_ALIASES["district_2"]),
        "bcr": _pick_first(flattened, _LAND_USE_ALIASES["bcr"]),
        "far": _pick_first(flattened, _LAND_USE_ALIASES["far"]),
        "height": _pick_first(flattened, _LAND_USE_ALIASES["height_limit_m"]),
    }


def _has_land_use_values(payload: dict[str, Any]) -> bool:
    return any(payload.get(key) for key in ("usedistrictnm", "usedistrict2nm", "bcr", "far", "height"))


def _fetch_land_use_properties_by_pnu(pnu: str, api_key: str) -> dict[str, Any]:
    errors: list[str] = []

    if api_key:
        try:
            response = httpx.get(
                EUM_LAND_USE_URL,
                params={"pnu": pnu, "serviceKey": api_key, "format": "json", "_type": "json"},
                headers={"Accept": "application/json, application/xml;q=0.9, text/xml;q=0.8"},
                timeout=20,
            )
            response.raise_for_status()
            parsed = extract_land_use_properties(response)
            if _has_land_use_values(parsed):
                return parsed
            errors.append("official EUM REST returned no usable zoning fields")
        except Exception as exc:
            errors.append(f"official EUM REST failed: {exc}")

    try:
        response = httpx.get(
            EUM_LAND_USE_GY_AJAX_URL,
            params={"pnu": pnu, "sggcd": pnu[:5], "carGbn": "GY", "ucodes": ""},
            timeout=20,
        )
        response.raise_for_status()
        parsed = extract_land_use_properties(response)
        if _has_land_use_values(parsed):
            return parsed
        errors.append("EUM HTML fallback returned no usable zoning fields")
    except Exception as exc:
        errors.append(f"EUM HTML fallback failed: {exc}")

    raise ValueError("; ".join(errors))


def _to_number(value: Any) -> float | None:
    if value in (None, ""):
        return None

    match = re.search(r"-?\d+(?:\.\d+)?", str(value).replace(",", ""))
    if not match:
        return None
    return float(match.group(0))


def query_land_info(*, address: str | None, pnu: str | None) -> dict:
    settings = get_settings()
    if not settings.vworld_api_key:
        return wrap_response(
            {
                "status": "disabled",
                "message": "VWORLD_API_KEY is missing. Land info lookup is disabled but the server remains available.",
                "required_keys": ["VWORLD_API_KEY"],
                "address": address,
                "pnu": pnu,
            },
            ProjectDomain.복합,
        )

    try:
        resolved = {"pnu": pnu, "parcel_address": address, "x": None, "y": None}
        if address and not pnu:
            resolved = _fetch_address_to_pnu(address, settings.vworld_api_key)
            pnu = resolved["pnu"]

        cadastral = _fetch_vworld_properties(CADASTRAL_LAYER, pnu, settings.vworld_api_key) if pnu else {}
        land_use: dict[str, Any] = {}
        warnings: list[str] = []

        if pnu:
            try:
                land_use = _fetch_land_use_properties_by_pnu(pnu, settings.data_go_kr_api_key)
            except Exception as exc:
                warnings.append(
                    f"Land use zoning could not be fetched from EUM. {exc}. Verify the parcel on eum.go.kr before filing."
                )

        land_price = _read_land_price_from_files(pnu)
        if land_price is None:
            warnings.append("Individual land price CSV has not been loaded into data/land_prices yet.")
        if not land_use:
            warnings.append("Land use zoning data is currently unavailable.")

        area = _to_number(cadastral.get("area") or cadastral.get("a2")) or 0
        bcr = _to_number(land_use.get("bcr"))
        far = _to_number(land_use.get("far"))

        return wrap_response(
            {
                "status": "success",
                "address": resolved.get("parcel_address") or address,
                "pnu": pnu,
                "land": {
                    "area_m2": area or None,
                    "jibmok": cadastral.get("jimok") or cadastral.get("jibmok"),
                    "ownership": cadastral.get("ownership"),
                },
                "zoning": {
                    "use_district": land_use.get("usedistrictnm"),
                    "district_2": land_use.get("usedistrict2nm"),
                    "bcr_pct": int(bcr) if bcr is not None else None,
                    "far_pct": int(far) if far is not None else None,
                    "height_limit_m": _to_number(land_use.get("height")),
                },
                "land_price": {
                    "individual_m2_won": land_price["individual_m2_won"] if land_price else None,
                    "total_won": round(land_price["individual_m2_won"] * area) if land_price and area else None,
                    "base_year": None,
                    "source": land_price["source"] if land_price else None,
                },
                "buildable": {
                    "max_floor_area_m2": round(area * (far / 100), 2) if area and far else None,
                    "max_building_coverage_m2": round(area * (bcr / 100), 2) if area and bcr else None,
                },
                "coordinates": {"x": resolved.get("x"), "y": resolved.get("y")},
                "warnings": warnings,
            },
            ProjectDomain.복합,
        )
    except Exception as exc:
        return wrap_response(
            {
                "status": "error",
                "message": str(exc),
                "address": address,
                "pnu": pnu,
                "note": "Check the VWorld key, address input, or local land price files.",
            },
            ProjectDomain.복합,
        )
