#!/usr/bin/env python3
"""Build the current Unity WebGL ``you_bl`` replacement bundles.

The current Mahjong Soul web client stores character illustrations in Unity
AssetBundles.  This script keeps the original bundle/object structure and only
replaces the ``full`` and ``bighead`` Texture2D payloads.
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

try:
    import UnityPy
    from PIL import Image
except ImportError as exc:  # pragma: no cover - command-line dependency hint
    raise SystemExit(
        "Missing build dependencies. Install them with:\n"
        "  python -m pip install UnityPy==1.25.2 Pillow"
    ) from exc


UNITY_VERSION = "2022.3.62f2"
RGBA32 = 4
SPINE_VERSION = "4.2.08"
SPINE_ATTACHMENT = "gys"

FULL_SIZE = (1114, 1311)
BIGHEAD_SIZE = (256, 256)
SPINE_PAGE_SIZE = (2048, 2048)
SPINE_REGION = (172, 0, 1704, 2048)

# Match the visible setup-pose bounds of the original you_bl skeleton. Keeping
# these values prevents the lobby's existing RectTransform/pivot logic from
# resizing or shifting the replacement unexpectedly.
SPINE_BOUNDS = (-1567.0758056640625, -0.3758544921875, 3248.82373046875, 3905.86376953125)
SPINE_ANIMATIONS = {
    "celebrate": 10.0,
    "celebrate_idle": 2.6666667461395264,
    "click": 7.333333492279053,
    "greeting": 8.666666984558105,
    "idle": 2.6666667461395264,
}

FULL_BUNDLE_NAME = (
    "uwv8ssu060e25j9j446uls$bm--bk0stggi__50508a0e23f24351e046.majset"
)
BIGHEAD_BUNDLE_NAME = (
    "uwv8ssu060e25j9j446uls$bm--bgonpnkojjlb_5faac359e4d487f14745.majset"
)
SPINE_DATA_BUNDLE_NAME = "9717zttvpmsxpw224u_04b9c3036a8264b25d79.majset"
SPINE_TEXTURE_BUNDLE_NAME = "9717zttvpmsxpw224v_b2374895f0746862c5da.majset"
BUNDLE_INFO_NAME = "bundle_info_so.majset"

FULL_ASSET_PATH = "myassets/deco/character/you_bl/full/full.png"
BIGHEAD_ASSET_PATH = "myassets/deco/character/you_bl/bighead/bighead.png"
SPINE_SKEL_ASSET_PATH = "myassets/spine/405906/you_bl.skel.txt"
SPINE_ATLAS_ASSET_PATH = "myassets/spine/405906/you_bl.atlas.txt"
SPINE_TEXTURE_ASSET_PATH = "myassets/spine/405906/you_bl.png"


class BinaryWriter:
    """Small writer for the subset of the Spine 4.2 binary format we need."""

    def __init__(self) -> None:
        self.data = bytearray()

    def byte(self, value: int) -> None:
        self.data.append(value & 0xFF)

    def boolean(self, value: bool) -> None:
        self.byte(1 if value else 0)

    def int32(self, value: int) -> None:
        self.data.extend(struct.pack(">i", value))

    def uint32(self, value: int) -> None:
        self.data.extend(struct.pack(">I", value & 0xFFFFFFFF))

    def float32(self, value: float) -> None:
        self.data.extend(struct.pack(">f", value))

    def varint(self, value: int, optimize_positive: bool = True) -> None:
        if not optimize_positive:
            value = (value << 1) ^ (value >> 31)
        value &= 0xFFFFFFFF
        while True:
            current = value & 0x7F
            value >>= 7
            if value:
                self.byte(current | 0x80)
            else:
                self.byte(current)
                return

    def string(self, value: str | None) -> None:
        if value is None:
            self.varint(0)
            return
        encoded = value.encode("utf-8")
        self.varint(len(encoded) + 1)
        self.data.extend(encoded)

    def string_ref(self, one_based_index: int) -> None:
        self.varint(one_based_index)


def _alpha_crop(image: Image.Image) -> Image.Image:
    image = image.convert("RGBA")
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("input image has no visible pixels")
    return image.crop(bbox)


def make_full_texture(source: Image.Image) -> Image.Image:
    """Fit the full character into the original transparent texture canvas."""
    character = _alpha_crop(source)
    max_width = round(FULL_SIZE[0] * 0.94)
    max_height = round(FULL_SIZE[1] * 0.96)
    character.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", FULL_SIZE, (0, 0, 0, 0))
    x = (FULL_SIZE[0] - character.width) // 2
    y = (FULL_SIZE[1] - character.height) // 2
    canvas.alpha_composite(character, (x, y))
    return canvas


def make_bighead_texture(source: Image.Image) -> Image.Image:
    """Crop the character head into the original square portrait texture."""
    source = source.convert("RGBA")
    bbox = source.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("input image has no visible pixels")

    left, top, right, bottom = bbox
    visible_width = right - left
    visible_height = bottom - top
    side = max(visible_width, round(visible_height * 0.62))
    center_x = (left + right) / 2
    crop_left = round(center_x - side / 2)
    crop_top = round(top - side * 0.04)

    # Pillow pads out-of-bounds crop pixels with transparency.
    crop = source.crop((crop_left, crop_top, crop_left + side, crop_top + side))
    return crop.resize(BIGHEAD_SIZE, Image.Resampling.LANCZOS)


def make_spine_page(source: Image.Image) -> Image.Image:
    """Create one atlas page while preserving the original skeleton bounds."""
    character = _alpha_crop(source)
    region_x, region_y, region_width, region_height = SPINE_REGION
    character.thumbnail((region_width, region_height), Image.Resampling.LANCZOS)

    page = Image.new("RGBA", SPINE_PAGE_SIZE, (0, 0, 0, 0))
    x = region_x + (region_width - character.width) // 2
    y = region_y + (region_height - character.height) // 2
    page.alpha_composite(character, (x, y))
    return page


def make_spine_atlas() -> str:
    x, y, width, height = SPINE_REGION
    page_width, page_height = SPINE_PAGE_SIZE
    return "\n".join(
        (
            "you_bl.png",
            f"size:{page_width},{page_height}",
            "filter:Linear,Linear",
            SPINE_ATTACHMENT,
            f"bounds:{x},{y},{width},{height}",
            f"offsets:0,0,{width},{height}",
            "",
        )
    )


def make_static_spine_skeleton() -> bytes:
    """Build a one-bone static skeleton with the original animation API."""
    writer = BinaryWriter()
    bound_x, bound_y, bound_width, bound_height = SPINE_BOUNDS

    writer.int32(0)
    writer.int32(0)
    writer.string(SPINE_VERSION)
    writer.float32(bound_x)
    writer.float32(bound_y)
    writer.float32(bound_width)
    writer.float32(bound_height)
    writer.float32(100)
    writer.boolean(False)

    writer.varint(1)
    writer.string(SPINE_ATTACHMENT)

    writer.varint(1)
    writer.string("root")
    for value in (0, 0, 0, 1, 1, 0, 0, 0):
        writer.float32(value)
    writer.byte(0)
    writer.boolean(False)

    writer.varint(1)
    writer.string(SPINE_ATTACHMENT)
    writer.varint(0)
    writer.uint32(0xFFFFFFFF)
    writer.int32(-1)
    writer.string_ref(1)
    writer.varint(0)

    for _ in range(4):
        writer.varint(0)

    writer.varint(1)
    writer.varint(0)
    writer.varint(1)
    writer.string_ref(1)
    writer.byte(0)
    writer.float32(bound_x + bound_width / 2)
    writer.float32(bound_y + bound_height / 2)
    writer.float32(1)
    writer.float32(1)
    writer.float32(bound_width)
    writer.float32(bound_height)

    writer.varint(0)
    writer.varint(0)

    writer.varint(len(SPINE_ANIMATIONS))
    for animation_name, duration in SPINE_ANIMATIONS.items():
        writer.string(animation_name)
        writer.varint(1)
        writer.varint(1)
        writer.varint(0)
        writer.varint(1)
        writer.byte(0)
        writer.varint(1)
        writer.float32(duration)
        writer.string_ref(1)
        for _ in range(8):
            writer.varint(0)

    return bytes(writer.data)


def replace_texture(
    source_bundle: Path,
    output_bundle: Path,
    object_name: str,
    asset_path: str,
    replacement: Image.Image,
) -> None:
    """Replace one Texture2D and save a validated LZ4 UnityFS bundle."""
    UnityPy.config.FALLBACK_UNITY_VERSION = UNITY_VERSION
    environment = UnityPy.load(str(source_bundle))

    matching_objects = []
    for obj in environment.objects:
        if obj.type.name != "Texture2D":
            continue
        data = obj.read()
        if data.m_Name == object_name:
            matching_objects.append(data)

    if len(matching_objects) != 1:
        raise ValueError(
            f"expected one Texture2D named {object_name!r} in {source_bundle}, "
            f"found {len(matching_objects)}"
        )

    texture = matching_objects[0]
    texture.set_image(replacement, target_format=RGBA32, mipmap_count=1)
    texture.save()

    output_bundle.parent.mkdir(parents=True, exist_ok=True)
    output_bundle.write_bytes(environment.file.save(packer="lz4"))

    # Reload the output to catch serialization/compression errors immediately.
    verified = UnityPy.load(str(output_bundle))
    if asset_path not in verified.container:
        raise ValueError(f"rebuilt bundle lost container path: {asset_path}")

    verified_textures = []
    for obj in verified.objects:
        if obj.type.name != "Texture2D":
            continue
        data = obj.read()
        if data.m_Name == object_name:
            verified_textures.append(data)

    if len(verified_textures) != 1:
        raise ValueError(f"could not reload Texture2D {object_name!r}")
    checked = verified_textures[0]
    if (checked.m_Width, checked.m_Height) != replacement.size:
        raise ValueError(
            f"unexpected rebuilt size: {(checked.m_Width, checked.m_Height)}"
        )
    if checked.m_TextureFormat != RGBA32:
        raise ValueError(f"unexpected texture format: {checked.m_TextureFormat}")


def replace_spine_data_bundle(
    source_bundle: Path,
    output_bundle: Path,
    skeleton: bytes,
    atlas: str,
) -> None:
    """Replace the binary skeleton and atlas TextAssets in their Unity bundle."""
    UnityPy.config.FALLBACK_UNITY_VERSION = UNITY_VERSION
    environment = UnityPy.load(str(source_bundle))

    replacements = {
        "you_bl.skel": skeleton.decode("utf-8", "surrogateescape"),
        "you_bl.atlas": atlas,
    }
    replaced = set()
    for obj in environment.objects:
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        if data.m_Name not in replacements:
            continue
        data.m_Script = replacements[data.m_Name]
        data.save()
        replaced.add(data.m_Name)

    if replaced != set(replacements):
        raise ValueError(f"missing Spine TextAssets: {set(replacements) - replaced}")

    output_bundle.parent.mkdir(parents=True, exist_ok=True)
    output_bundle.write_bytes(environment.file.save(packer="lz4"))

    verified = UnityPy.load(str(output_bundle))
    for path in (SPINE_SKEL_ASSET_PATH, SPINE_ATLAS_ASSET_PATH):
        if path not in verified.container:
            raise ValueError(f"rebuilt Spine bundle lost container path: {path}")

    verified_payloads = {}
    for obj in verified.objects:
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        if data.m_Name in replacements:
            verified_payloads[data.m_Name] = data.m_Script

    verified_skeleton = verified_payloads["you_bl.skel"].encode(
        "utf-8", "surrogateescape"
    )
    if verified_skeleton != skeleton:
        raise ValueError("Spine skeleton changed during bundle serialization")
    if verified_payloads["you_bl.atlas"] != atlas:
        raise ValueError("Spine atlas changed during bundle serialization")


def replace_bundle_info(
    source_bundle: Path,
    output_bundle: Path,
    bundle_sizes: dict[str, int],
) -> None:
    """Update generated bundle sizes in the current BundleInfoSO manifest."""
    UnityPy.config.FALLBACK_UNITY_VERSION = UNITY_VERSION
    environment = UnityPy.load(str(source_bundle))
    manifest = next(
        obj for obj in environment.objects if obj.type.name == "MonoBehaviour"
    )
    tree = manifest.read_typetree()

    updated = set()
    for info in tree["bundleInfos"]:
        name = info["name"]
        if name not in bundle_sizes:
            continue
        info["fileSize"] = bundle_sizes[name]
        updated.add(name)

    if updated != set(bundle_sizes):
        raise ValueError(f"manifest is missing bundles: {set(bundle_sizes) - updated}")

    manifest.save_typetree(tree)
    output_bundle.parent.mkdir(parents=True, exist_ok=True)
    output_bundle.write_bytes(environment.file.save(packer="lz4"))

    verified = UnityPy.load(str(output_bundle))
    checked_manifest = next(
        obj for obj in verified.objects if obj.type.name == "MonoBehaviour"
    ).read_typetree()
    checked_sizes = {
        info["name"]: info["fileSize"]
        for info in checked_manifest["bundleInfos"]
        if info["name"] in bundle_sizes
    }
    if checked_sizes != bundle_sizes:
        raise ValueError(
            f"manifest size verification failed: {checked_sizes} != {bundle_sizes}"
        )


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    default_output = script_dir.parents[1] / "assetbundles" / "DXT"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--image",
        type=Path,
        default=script_dir / "gys-transparent.png",
        help="transparent full-body PNG",
    )
    parser.add_argument(
        "--full-source",
        type=Path,
        default=script_dir / "source" / "original-full.majset",
    )
    parser.add_argument(
        "--bighead-source",
        type=Path,
        default=script_dir / "source" / "original-bighead.majset",
    )
    parser.add_argument(
        "--spine-data-source",
        type=Path,
        default=script_dir / "source" / SPINE_DATA_BUNDLE_NAME,
    )
    parser.add_argument(
        "--spine-texture-source",
        type=Path,
        default=script_dir / "source" / SPINE_TEXTURE_BUNDLE_NAME,
    )
    parser.add_argument(
        "--bundle-info-source",
        type=Path,
        default=script_dir / "source" / "original-bundle-info.majset",
    )
    parser.add_argument("--output-dir", type=Path, default=default_output)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent

    for path in (
        args.image,
        args.full_source,
        args.bighead_source,
        args.spine_data_source,
        args.spine_texture_source,
        args.bundle_info_source,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)

    source = Image.open(args.image).convert("RGBA")
    full = make_full_texture(source)
    bighead = make_bighead_texture(source)
    spine_page = make_spine_page(source)
    spine_atlas = make_spine_atlas()
    spine_skeleton = make_static_spine_skeleton()

    full.save(script_dir / "preview-full.png")
    bighead.save(script_dir / "preview-bighead.png")
    spine_page.save(script_dir / "preview-spine-page.png")
    (script_dir / "preview-spine.atlas.txt").write_text(
        spine_atlas, encoding="utf-8", newline="\n"
    )
    (script_dir / "preview-spine.skel.txt").write_bytes(spine_skeleton)

    full_output = args.output_dir / FULL_BUNDLE_NAME
    bighead_output = args.output_dir / BIGHEAD_BUNDLE_NAME
    spine_data_output = args.output_dir / SPINE_DATA_BUNDLE_NAME
    spine_texture_output = args.output_dir / SPINE_TEXTURE_BUNDLE_NAME
    bundle_info_output = args.output_dir / BUNDLE_INFO_NAME
    replace_texture(
        args.full_source,
        full_output,
        "full",
        FULL_ASSET_PATH,
        full,
    )
    replace_texture(
        args.bighead_source,
        bighead_output,
        "bighead",
        BIGHEAD_ASSET_PATH,
        bighead,
    )
    replace_spine_data_bundle(
        args.spine_data_source,
        spine_data_output,
        spine_skeleton,
        spine_atlas,
    )
    replace_texture(
        args.spine_texture_source,
        spine_texture_output,
        "you_bl",
        SPINE_TEXTURE_ASSET_PATH,
        spine_page,
    )
    generated_outputs = (
        full_output,
        bighead_output,
        spine_data_output,
        spine_texture_output,
    )
    replace_bundle_info(
        args.bundle_info_source,
        bundle_info_output,
        {output.name: output.stat().st_size for output in generated_outputs},
    )

    print("Built and verified:")
    for output in (*generated_outputs, bundle_info_output):
        print(f"  {output} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
