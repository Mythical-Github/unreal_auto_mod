from __future__ import annotations

import getpass
import os
import re
import shutil
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING
import json

if TYPE_CHECKING:
    from pathlib import Path

from unreal_auto_mod import data_structures, logger, utilities

# This module does not account for when collections are across
# different collections directories, like local, shared, and private
# ones. It is mainly for use with a singular collections directory,
# but most functions will work across both. However, things relating
# to ancestors and descendants may fail.
#
# A content line refers to:
# - For a dynamic collection: a filter line.
# - For a static collection: an asset path line.


# Issues:
# lots of extra spaces can end up in the config
# duplicate lines can end up in the content lines, this means the check if in lines checks are off
# dynamic/static using the proper content_lines/filter_lines/unreal_asset_path_lines is bugged right now
# when passing a path/to/file/file.uasset to unreal asset path it doesn't remove the extension before it makes the full file path
# when passed in test.txt it will return test.txt.test.txt instead of test.test


class UnrealGuid:
    """
    A class representing an Unreal Engine GUID (Globally Unique Identifier).

    Attributes:
        uid (str): The unique identifier (GUID) in uppercase format.

    Methods:
        __repr__() -> str: Returns the GUID as a string representation.
        generate_unreal_guid() -> str: Static method to generate a new UUID and return it as a string in uppercase format.
        to_uid() -> str: Returns the GUID as a string.
        from_uid(uid: str) -> UnrealGuid: Class method to create an UnrealGuid object from a given UID string.
    """

    def __init__(self, uid: str):
        """
        Initializes the UnrealGuid with a given UID string or generates a new one if not provided.

        Args:
            uid (str, optional): A string representing the GUID. If not provided, a new GUID is generated.
        """
        if uid:
            self.uid = uid.upper()
        else:
            self.uid = self.generate_unreal_guid()

    def __repr__(self) -> str:
        """
        Returns the GUID as a string representation.

        Returns:
            str: The GUID in uppercase format.
        """
        return self.uid

    @staticmethod
    def generate_unreal_guid() -> str:
        """
        Generates a new UUID (GUID) and returns it as a string in uppercase format.

        Returns:
            str: The generated UUID in uppercase.
        """
        return str(uuid.uuid4()).upper()

    def to_uid(self) -> str:
        """
        Returns the GUID as a string.

        Returns:
            str: The GUID.
        """
        return self.uid

    @classmethod
    def from_uid(cls, uid: str) -> UnrealGuid:
        """
        Creates an UnrealGuid object from a given UID string, converting it to uppercase.

        Args:
            uid (str): The GUID string to convert to an UnrealGuid object.

        Returns:
            UnrealGuid: A new UnrealGuid object created from the provided UID string.
        """
        return cls(uid.upper())


class UnrealCollectionColor:
    """
    A class representing a color with red, green, blue, and alpha components.

    Can be initialized with either RGBA float values or a formatted string.
    """

    def __init__(self, r, g=None, b=None, a=None):
        """
        Initializes the color with either RGBA float values or a formatted string.

        Args:
            r (float or str): The red component (0.0 to 1.0) or a formatted string.
            g (float, optional): The green component (0.0 to 1.0).
            b (float, optional): The blue component (0.0 to 1.0).
            a (float, optional): The alpha (opacity) component (0.0 to 1.0).

        Raises:
            ValueError: If the formatted string is invalid.
        """
        if isinstance(r, str):
            self.r, self.g, self.b, self.a = self._parse_string(r)
        else:
            self.r = self._clamp(r)
            self.g = self._clamp(g)
            self.b = self._clamp(b)
            self.a = self._clamp(a)

    @staticmethod
    def _parse_string(color_string):
        """
        Parses a formatted color string into its RGBA components as floats.

        Args:
            color_string (str): The color string in the format "(R=0.250000,G=0.018259,B=0.000337,A=1.000000)".

        Returns:
            tuple: (r, g, b, a) as floats.

        Raises:
            ValueError: If the format is invalid.
        """
        match = re.match(
            r"\(R=([\d.]+),G=([\d.]+),B=([\d.]+),A=([\d.]+)\)", color_string
        )
        if not match:
            invalid_color_string_format_error = (
                f"Invalid color string format: {color_string}"
            )
            raise ValueError(invalid_color_string_format_error)
        return tuple(map(float, match.groups()))

    @staticmethod
    def _clamp(value):
        """Ensures the color component stays within [0.0, 1.0]."""
        return max(0.0, min(1.0, value))

    def get_formatted_string(self) -> str:
        """Returns the color components as a formatted string."""
        return f"(R={self.r:.6f},G={self.g:.6f},B={self.b:.6f},A={self.a:.6f})"

    def __repr__(self) -> str:
        """Returns the color as a formatted string for easy inspection."""
        return self.get_formatted_string()


class UnrealAssetPath:
    """
    A class for managing Unreal Engine asset paths and references.

    Attributes:
        normalized_path (str): The normalized asset path with forward slashes.
        asset_reference (str): The full asset reference in the format "/path/to/asset.AssetName".

    Methods:
        normalize_path(path: str) -> str: Normalizes the provided path by replacing backslashes with forward slashes and trimming any surrounding slashes.
        to_asset_reference() -> str: Converts the normalized path into an asset reference in the format "/path/to/asset.AssetName".
        from_asset_reference() -> str: Extracts and returns the asset path from the asset reference (removes the asset name).
        __repr__() -> str: Returns the asset reference as a string representation.
    """

    def __init__(self, path: str):
        """
        Initializes the UnrealAssetPath with the given asset path.

        Args:
            path (str): The path to the asset, which will be normalized and converted into an asset reference.
        """
        self.normalized_path = self.normalize_path(path)
        self.asset_reference = self.to_asset_reference()

    def normalize_path(self, path: str) -> str:
        """
        Normalizes the provided asset path by replacing backslashes with forward slashes and trimming surrounding slashes.

        Args:
            path (str): The asset path to normalize.

        Returns:
            str: The normalized path with forward slashes and no surrounding slashes.
        """
        path = path.replace("\\", "/").strip("/")
        return f"/{path}"

    def to_asset_reference(self) -> str:
        """
        Converts the normalized path into an asset reference in the format "/path/to/asset.AssetName".

        Returns:
            str: The asset reference including both the normalized path and asset name.
        """
        asset_name = self.normalized_path.split("/")[-1]
        return f"{self.normalized_path}.{asset_name}"

    def from_asset_reference(self) -> str:
        """
        Extracts and returns the asset path from the asset reference (removes the asset name).

        Returns:
            str: The asset path without the asset name (e.g., "/path/to/asset").
        """
        if "." in self.asset_reference:
            path, _ = self.asset_reference.rsplit(".", 1)
            return path
        return self.asset_reference

    @staticmethod
    def static_from_asset_reference(asset_reference: str) -> str:
        """
        Extracts and returns the asset path from the asset reference (removes the asset name).

        Args:
            asset_reference (str): The full asset reference path.

        Returns:
            str: The asset path without the asset name (e.g., "/path/to/asset").
        """
        return (
            asset_reference.rsplit(".", 1)[0]
            if "." in asset_reference
            else asset_reference
        )

    def __repr__(self) -> str:
        """
        Returns the asset reference as a string representation.

        Returns:
            str: The asset reference in string format.
        """
        return self.asset_reference


class UnrealContentLineType(Enum):
    STATIC = "Static"
    DYNAMIC = "Dynamic"


class UnrealCollectionType(Enum):
    LOCAL = "local"
    SHARED = "shared"
    PRIVATE = "private"


@dataclass
class UnrealCollection:
    file_system_path: Path
    file_version: int
    content_type: UnrealContentLineType
    parent_guid: UnrealGuid
    guid: UnrealGuid
    color: UnrealCollectionColor
    content_lines: list[UnrealAssetPath] | list[str]


def are_any_collections_in_use_in_collections_directory(
    collections_directory: Path,
) -> bool:
    return get_number_of_collections_in_collections_directory(collections_directory) > 0


def get_number_of_collections_in_collections_directory(
    collections_directory: Path,
) -> int:
    return len(get_enabled_collections(collections_directory))


def get_local_collections_directory(
    uproject_directory: Path, *, create_directory_if_missing: bool = True
) -> Path:
    collections_directory = os.path.normpath(f"{uproject_directory}/Saved/Collections")
    if create_directory_if_missing and not os.path.isdir(collections_directory):
        os.makedirs(collections_directory)
    return Path(collections_directory)


def get_private_collections_directory(
    uproject_directory: Path,
    *,
    create_directory_if_missing: bool = True,
    developer_name: str = getpass.getuser(),
) -> Path:
    collections_directory = os.path.normpath(
        f"{uproject_directory}/Content/Developers/{developer_name}/Collections"
    )
    if create_directory_if_missing and not os.path.isdir(collections_directory):
        os.makedirs(collections_directory)
    return Path(collections_directory)


def get_shared_collections_directory(
    uproject_directory: Path, *, create_directory_if_missing: bool = True
) -> Path:
    collections_directory = os.path.normpath(
        f"{uproject_directory}/Content/Collections"
    )
    if create_directory_if_missing and not os.path.isdir(collections_directory):
        os.makedirs(collections_directory)
    return Path(collections_directory)


def get_unreal_collection_from_unreal_collection_path(
    collection_path: Path,
) -> UnrealCollection:
    if not os.path.isfile(collection_path):
        unreal_collection_path_does_not_exist_error = (
            f'The following collection path file does not exist "{collection_path}"'
        )
        raise FileNotFoundError(unreal_collection_path_does_not_exist_error)
    new_content_lines = []
    for line in get_all_non_key_lines_from_collection_path(collection_path):
        new_content_lines.append(UnrealAssetPath(path=line))
    collection_to_return = UnrealCollection(
        file_system_path=collection_path,
        file_version=get_file_version_from_collection_path(collection_path),
        content_type=get_type_from_unreal_collection_path(collection_path),
        parent_guid=get_parent_guid_from_unreal_collection_path(collection_path),
        guid=get_guid_from_unreal_collection_path(collection_path),
        color=get_collection_color_from_unreal_collection_path(collection_path),
        content_lines=new_content_lines,
    )
    if collection_to_return is None:
        raise RuntimeError
    return collection_to_return


def get_enabled_collection_paths(collections_directory: Path) -> list[Path]:
    return filter_by_extension(get_files_in_dir(collections_directory), ".collection")


def get_disabled_collection_paths(collections_directory: Path) -> list[Path]:
    return filter_by_extension(
        get_files_in_dir(collections_directory), ".collection.disabled"
    )


def get_all_collection_paths(collections_directory: Path) -> list[Path]:
    collection_paths = []
    collection_paths.extend(get_enabled_collection_paths(collections_directory))
    collection_paths.extend(get_disabled_collection_paths(collections_directory))
    return collection_paths


def get_enabled_collections(collections_directory: Path) -> list[UnrealCollection]:
    return prune_disabled_parents(
        [
            get_unreal_collection_from_unreal_collection_path(unreal_collection_path)
            for unreal_collection_path in get_enabled_collection_paths(
                collections_directory
            )
        ],
        collections_directory,
    )


def get_disabled_collections(collections_directory: Path) -> list[UnrealCollection]:
    return [
        get_unreal_collection_from_unreal_collection_path(unreal_collection_path)
        for unreal_collection_path in get_disabled_collection_paths(
            collections_directory
        )
    ]


def has_disabled_parent(
    collection: UnrealCollection,
    collections: list[UnrealCollection],
    disabled_guids: set[UnrealGuid],
) -> bool:
    parent_guid = collection.parent_guid
    while parent_guid:
        if parent_guid in disabled_guids:
            return True
        parent = next((col for col in collections if col.guid == parent_guid), None)
        parent_guid = parent.parent_guid if parent else None
    return False


def prune_disabled_parents(
    collections: list[UnrealCollection], collections_directory: Path
) -> list[UnrealCollection]:
    disabled_guids = {
        col.guid for col in get_disabled_collections(collections_directory)
    }
    return [
        col
        for col in collections
        if not has_disabled_parent(col, collections, disabled_guids)
    ]


def get_all_collections(collections_directory: Path) -> list[UnrealCollection]:
    unreal_collections = []
    unreal_collections.extend(get_enabled_collections(collections_directory))
    unreal_collections.extend(get_disabled_collections(collections_directory))
    return unreal_collections


def get_parent_collection(
    collection: UnrealCollection, collections_directory: Path
) -> UnrealCollection:
    parent_collection_file = None
    parent_guid = get_parent_guid_from_unreal_collection_path(
        collection.file_system_path
    )
    if parent_guid and parent_guid != get_blank_unreal_guid():
        all_collection_files = get_enabled_collections(collections_directory)
        for collection_file in all_collection_files:
            if (
                get_guid_from_unreal_collection_path(collection_file.file_system_path)
                == parent_guid
            ):
                parent_collection_file = collection_file
                break
    if parent_collection_file:
        return parent_collection_file
    else:
        collection_error = "parent collection was none"
        raise RuntimeError(collection_error)


def get_file_version_from_collection_path(collection_path: Path) -> int:
    config_not_found_error = (
        f'No file exists at the following provided collection path "{collection_path}".'
    )
    if not os.path.isfile(collection_path):
        raise FileNotFoundError(config_not_found_error)
    config_lines = get_all_lines_in_config(str(collection_path))
    config_line_prefix = "FileVersion:"

    for line in config_lines:
        if line.strip("\n").startswith(config_line_prefix):
            return int(line.strip("\n").replace(config_line_prefix, ""))

    config_error = f'There was no "{config_line_prefix}" line in the following config "{collection_path}"'
    raise RuntimeError(config_error)


def get_type_from_unreal_collection_path(
    collection_path: Path,
) -> UnrealContentLineType:
    config_not_found_error = (
        f'No file exists at the following provided collection path "{collection_path}".'
    )
    if not os.path.isfile(collection_path):
        raise FileNotFoundError(config_not_found_error)
    config_lines = get_all_lines_in_config(str(collection_path))
    config_line_prefix = "Type:"

    for line in config_lines:
        if line.strip("\n").startswith(config_line_prefix):
            return UnrealContentLineType(
                data_structures.get_enum_from_val(
                    UnrealContentLineType,
                    line.strip("\n").replace(config_line_prefix, ""),
                )
            )

    config_error = f'There is no "{config_line_prefix}" line in the following config "{collection_path}"'
    raise RuntimeError(config_error)


def get_guid_from_unreal_collection_path(collection_path: Path) -> UnrealGuid:
    config_not_found_error = (
        f'No file exists at the following provided collection path "{collection_path}".'
    )
    if not os.path.isfile(collection_path):
        raise FileNotFoundError(config_not_found_error)
    config_lines = get_all_lines_in_config(str(collection_path))
    config_line_prefix = "Guid:"

    for line in config_lines:
        if line.strip("\n").startswith(config_line_prefix):
            return UnrealGuid(line.strip("\n").replace(config_line_prefix, ""))

    config_error = f'There is no "{config_line_prefix}" line in the following config "{collection_path}"'
    raise RuntimeError(config_error)


def get_parent_guid_from_unreal_collection_path(collection_path: Path) -> UnrealGuid:
    config_not_found_error = (
        f'No file exists at the following provided collection path "{collection_path}".'
    )
    if not os.path.isfile(collection_path):
        raise FileNotFoundError(config_not_found_error)
    config_lines = get_all_lines_in_config(str(collection_path))
    config_line_prefix = "ParentGuid:"

    for line in config_lines:
        if line.strip("\n").startswith(config_line_prefix):
            return UnrealGuid(line.strip("\n").replace(config_line_prefix, ""))

    config_error = f'There is no "{config_line_prefix}" line in the following config "{collection_path}"'
    raise RuntimeError(config_error)


def get_collection_color_from_unreal_collection_path(
    collection_path: Path,
) -> UnrealCollectionColor:
    config_not_found_error = (
        f'No file exists at the following provided collection path "{collection_path}".'
    )
    if not os.path.isfile(collection_path):
        raise FileNotFoundError(config_not_found_error)
    config_lines = get_all_lines_in_config(str(collection_path))
    config_line_prefix = "Color:"

    for line in config_lines:
        if line.strip("\n").startswith(config_line_prefix):
            return UnrealCollectionColor(
                line.strip("\n").replace(config_line_prefix, "")
            )

    config_error = f'There is no "{config_line_prefix}" line in the following config "{collection_path}"'
    raise RuntimeError(config_error)


def add_content_lines_to_collection(
    collection: UnrealCollection, content_lines: list[UnrealAssetPath] | list[str]
):
    for content_line in content_lines:
        add_content_line_to_collection(collection, content_line)


def remove_content_lines_from_collection(
    collection: UnrealCollection, content_lines: list[UnrealAssetPath] | list[str]
):
    for content_line in content_lines:
        remove_content_line_from_collection(collection, content_line)


def rename_collection_from_collection(collection: UnrealCollection, new_name: str):
    src_path = collection.file_system_path
    dst_path = os.path.normpath(f"{os.path.dirname(src_path)}/{new_name}.collection")
    if not os.path.isfile(src_path):
        not_found_error = (
            f'The following collection file to be renamed was not found "{src_path}"'
        )
        raise FileNotFoundError(not_found_error)
    if os.path.isfile(dst_path):
        dupe_name_error = f'The following collection already exists, so you cannot rename one to that "{dst_path}".'
        raise FileExistsError(dupe_name_error)
    shutil.move(src_path, dst_path)


def rename_collection_from_collection_path(collection_path: Path, new_name: str):
    dst_path = os.path.normpath(
        f"{os.path.dirname(collection_path)}/{new_name}.collection"
    )
    if not os.path.isfile(collection_path):
        not_found_error = f'The following collection file to be renamed was not found "{collection_path}"'
        raise FileNotFoundError(not_found_error)
    if os.path.isfile(dst_path):
        dupe_name_error = f'The following collection already exists, so you cannot rename one to that "{dst_path}".'
        raise FileExistsError(dupe_name_error)
    shutil.move(collection_path, dst_path)


def delete_collection(collection: UnrealCollection | str):
    collection_path = collection
    if isinstance(collection, UnrealCollection):
        collection_path = collection.file_system_path
    elif isinstance(collection, str):
        collection_path = collection

    if os.path.isfile(collection_path):
        os.remove(collection_path)
    else:
        no_collection_to_delete_error = f'The following collection file to be deleted was not found: "{collection_path}"'
        raise FileNotFoundError(no_collection_to_delete_error)


def get_all_key_lines_from_collection_path(collection_path: Path) -> list[str]:
    if not os.path.isfile(str(collection_path)):
        no_collection_found_error = f'No file exists at the following provided collection path "{collection_path}".'
        raise FileNotFoundError(no_collection_found_error)

    config_lines = get_all_lines_in_config(str(collection_path))

    key_start_sub_strings = ["FileVersion:", "Type:", "Guid:", "ParentGuid:", "Color:"]

    return [
        line.strip()
        for line in config_lines
        if any(
            line.strip().startswith(sub_string) for sub_string in key_start_sub_strings
        )
    ]


def get_all_non_key_lines_from_collection_path(collection_path: Path) -> list[str]:
    if not os.path.isfile(str(collection_path)):
        no_collection_error = f'No file exists at the following provided collection path "{collection_path}".'
        raise FileNotFoundError(no_collection_error)

    config_lines = get_all_lines_in_config(str(collection_path))

    removal_start_sub_strings = [
        "FileVersion:",
        "Type:",
        "Guid:",
        "ParentGuid:",
        "Color:",
    ]

    return [
        line.strip()
        for line in config_lines
        if not any(
            line.strip().startswith(sub_string)
            for sub_string in removal_start_sub_strings
        )
    ]


def get_blank_unreal_guid() -> UnrealGuid:
    return UnrealGuid(uid="00000000-0000-0000-0000-000000000000")


def set_collection_parent_collection(
    parent_collection: UnrealCollection,
    collections_directory: Path,
    child_collection: UnrealCollection,
):
    set_collection_parent_guid(
        child_collection, collections_directory, parent_collection.guid
    )


def add_child_collection_to_parent_collection(
    parent_collection: UnrealCollection,
    collections_directory: Path,
    child_collection: UnrealCollection,
):
    set_collection_parent_guid(
        child_collection, collections_directory, parent_collection.guid
    )


def add_child_collections_to_parent_collection(
    child_collections: list[UnrealCollection],
    collections_directory,
    parent_collection: UnrealCollection,
):
    for collection in child_collections:
        set_collection_parent_guid(
            collection, collections_directory, parent_collection.guid
        )


def remove_child_collection_from_parent_collection(
    child_collection: UnrealCollection, collections_directory: Path
):
    set_collection_parent_guid(
        child_collection,
        collections_directory,
        UnrealGuid(UnrealGuid.generate_unreal_guid()),
    )


def remove_child_collections_from_parent_collection(
    child_collections: list[UnrealCollection], collections_directory: Path
):
    for collection in child_collections:
        set_collection_parent_guid(
            collection,
            collections_directory,
            UnrealGuid(UnrealGuid.generate_unreal_guid()),
        )


def create_collection(
    collection_name: str,
    collections_directory: Path,
    file_version: int,
    collection_type: UnrealContentLineType,
    guid: UnrealGuid,
    parent_guid: UnrealGuid,
    color: UnrealCollectionColor,
    content_lines: list[UnrealAssetPath] | list[str],
    *,
    exist_ok: bool,
):
    new_content_lines = []
    if isinstance(content_lines, list) and all(
        isinstance(x, str) for x in content_lines
    ):
        for content_line in content_lines:
            new_content_lines.append(UnrealAssetPath(path=str(content_line)))
    else:
        new_content_lines = content_lines
    collection_path = os.path.normpath(f"{collections_directory}/{collection_name}")
    if os.path.isfile(collection_path) and not exist_ok:
        collection_exists_error = (
            f'The following collection file already exists: "{collection_path}"'
        )
        raise FileExistsError(collection_exists_error)
    unreal_collection = UnrealCollection(
        file_system_path=Path(
            os.path.normpath(f"{collections_directory}/{collection_name}")
        ),
        file_version=file_version,
        content_type=collection_type,
        guid=guid,
        parent_guid=parent_guid,
        color=color,
        content_lines=content_lines,
    )
    unreal_collection_file_system_path = unreal_collection.file_system_path
    if os.path.isfile(unreal_collection_file_system_path):
        if exist_ok:
            os.remove(unreal_collection_file_system_path)
        else:
            already_exists_error = f'A collection file already exists at "{unreal_collection_file_system_path}"'
            raise FileExistsError(already_exists_error)
    save_unreal_collection_to_file(unreal_collection)


def enable_collection(
    collection: UnrealCollection, *, disabled_collection_exists_ok: bool = True
):
    # does not account for descendants
    enabled_collection_path = os.path.splitext(
        os.path.normpath(collection.file_system_path)
    )[0]
    disabled_collection_path = os.path.normpath(f"{enabled_collection_path}.disabled")
    if not os.path.isfile(disabled_collection_path):
        disabled_collection_path_does_not_exist_error = f'The following collection file does not exist "{disabled_collection_path}", so it cannot be enabled.'
        raise FileNotFoundError(disabled_collection_path_does_not_exist_error)
    if os.path.isfile(enabled_collection_path):
        if disabled_collection_exists_ok:
            os.remove(enabled_collection_path)
        else:
            enabled_file_already_exists_error = f'The following file exists already "{enabled_collection_path}", so a file cannot be backed up in the same place.'
            raise FileExistsError(enabled_file_already_exists_error)
    shutil.move(disabled_collection_path, enabled_collection_path)
    if isinstance(collection, UnrealCollection):
        collection.file_system_path = Path(enabled_collection_path)


def disable_collection(
    collection: UnrealCollection | str, *, disabled_collection_exists_ok: bool = True
):
    # does not account for descendants
    if isinstance(collection, UnrealCollection):
        collection = str(collection.file_system_path)
    disabled_collection_path = os.path.normpath(f"{collection}.disabled")
    enabled_collection_path = os.path.normpath(collection)
    if not os.path.isfile(enabled_collection_path):
        disabled_collection_path_does_not_exist_error = f'The following collection file does not exist "{enabled_collection_path}", so it cannot be disabled.'
        raise FileNotFoundError(disabled_collection_path_does_not_exist_error)
    if os.path.isfile(disabled_collection_path):
        if disabled_collection_exists_ok:
            os.remove(disabled_collection_path)
        else:
            enabled_file_already_exists_error = f'The following file exists already "{disabled_collection_path}", so a file cannot be moved to the same place.'
            raise FileExistsError(enabled_file_already_exists_error)
    shutil.move(enabled_collection_path, disabled_collection_path)
    if isinstance(collection, UnrealCollection):
        collection.file_system_path = Path(disabled_collection_path)


def set_collection_guid_from_collection(
    collection: UnrealCollection,
    collections_directory: Path,
    new_guid: UnrealGuid,
    *,
    fix_child_collections_parent_guids: bool = True,
):
    original_collection_guid = get_guid_from_unreal_collection_path(
        collection.file_system_path
    )
    all_collection_paths = get_all_collection_paths(collections_directory)
    all_collection_guids = [
        get_guid_from_unreal_collection_path(path) for path in all_collection_paths
    ]
    if new_guid in all_collection_guids:
        guid_already_in_use_error = ""
        raise RuntimeError(guid_already_in_use_error)
    if fix_child_collections_parent_guids:
        for path in all_collection_paths:
            if original_collection_guid == get_parent_guid_from_unreal_collection_path(
                path
            ):
                get_unreal_collection_from_unreal_collection_path(
                    path
                ).parent_guid = new_guid
    collection.guid = new_guid
    save_unreal_collection_to_file(collection)


def set_collection_parent_guid(
    collection: UnrealCollection,
    collections_directory: Path,
    new_guid: UnrealGuid = UnrealGuid(UnrealGuid.generate_unreal_guid()),
):
    all_collection_paths = get_all_collection_paths(collections_directory)
    parent_exists = False

    for path in all_collection_paths:
        other_collection = get_unreal_collection_from_unreal_collection_path(path)
        if new_guid == other_collection.parent_guid:
            parent_exists = True
            break

    if not parent_exists:
        parent_guid_not_found_error = (
            f'No collection has the parent_guid "{new_guid}" set as its guid.'
        )
        raise RuntimeError(parent_guid_not_found_error)

    collection.parent_guid = new_guid
    save_unreal_collection_to_file(collection)


def set_collection_color(
    collection: UnrealCollection,
    r_color: float,
    g_color: float,
    b_color: float,
    a_color: float,
):
    collection.color = UnrealCollectionColor(r=r_color, g=g_color, b=b_color, a=a_color)
    save_unreal_collection_to_file(collection)


def add_content_line_to_collection(
    collection: UnrealCollection, content_line: UnrealAssetPath | str
):
    if content_line not in collection.content_lines:
        collection.content_lines.append(content_line)  # pyright: ignore
        save_unreal_collection_to_file(collection)


def get_child_collections(
    collection: UnrealCollection, collections_directory: Path
) -> list[UnrealCollection]:
    parent_guid = collection.parent_guid
    child_collections = []
    all_collection_paths = get_all_collection_paths(collections_directory)
    for collection_path in all_collection_paths:
        other_collection = get_unreal_collection_from_unreal_collection_path(
            collection_path
        )
        if other_collection.guid == parent_guid:
            child_collections.append(other_collection)
    return child_collections


def remove_content_line_from_collection(
    collection: UnrealCollection, line_to_remove: UnrealAssetPath | str
):
    if line_to_remove in collection.content_lines:
        collection.content_lines.remove(line_to_remove)  # pyright: ignore
        save_unreal_collection_to_file(collection)


def set_collection_type(
    collection: UnrealCollection, collection_type: UnrealContentLineType
):
    if collection.content_type != collection_type:
        collection.content_type = collection_type
        save_unreal_collection_to_file(collection)


def set_collection_file_version(collection: UnrealCollection, file_version: int):
    if collection.file_version != file_version:
        collection.file_version = file_version
        save_unreal_collection_to_file(collection)


def set_config_key_and_value_from_collection_path(
    collection_path: Path, key: str, value: str
):
    config_lines = get_all_lines_in_config(str(collection_path))

    updated_lines = []
    value_set = False

    for line in config_lines:
        if line.startswith(key):
            updated_lines.append(f"{key}{value}\n")
            value_set = True
        else:
            updated_lines.append(line)

    if not value_set:
        updated_lines.insert(0, f"{key}{value}\n")

    set_all_lines_in_config(str(collection_path), updated_lines)


def set_file_version_from_collection_path(collection_path: Path, file_version: int):
    set_config_key_and_value_from_collection_path(
        collection_path=Path(collection_path),
        key="FileVersion:",
        value=str(file_version),
    )


def set_collection_type_from_collection_path(
    collection_path: Path, collection_type: UnrealContentLineType
):
    set_config_key_and_value_from_collection_path(
        collection_path=Path(collection_path), key="Type:", value=collection_type.value
    )


def set_guid_from_collection_path(collection_path: Path, guid: UnrealGuid):
    set_config_key_and_value_from_collection_path(
        collection_path=Path(collection_path), key="Guid:", value=str(guid)
    )


def set_parent_guid_from_collection_path(
    collection_path: Path, parent_guid: UnrealGuid
):
    set_config_key_and_value_from_collection_path(
        collection_path=Path(collection_path), key="ParentGuid:", value=str(parent_guid)
    )


def set_color_from_collection_path(
    collection_path: Path, unreal_color: UnrealCollectionColor
):
    set_config_key_and_value_from_collection_path(
        collection_path=Path(collection_path),
        key="Color:",
        value=unreal_color.get_formatted_string(),
    )


def set_content_lines_from_collection_path(
    collection_path: Path, unreal_asset_paths: list[UnrealAssetPath] | list[str]
):
    all_key_lines = get_all_key_lines_from_collection_path(Path(collection_path))

    formatted_lines = [line + "\n" for line in all_key_lines]
    formatted_lines.append("\n")
    formatted_lines.extend(
        [str(unreal_asset_path) + "\n" for unreal_asset_path in unreal_asset_paths]
    )

    set_all_lines_in_config(str(collection_path), formatted_lines)


def save_unreal_collection_to_file(
    unreal_collection: UnrealCollection, *, exist_ok: bool = True
):
    if not exist_ok and os.path.isfile(unreal_collection.file_system_path):
        collection_already_exists_error = f'The following collection file already exists "{unreal_collection.file_system_path}".'
        raise FileExistsError(collection_already_exists_error)
    set_color_from_collection_path(
        unreal_collection.file_system_path, unreal_collection.color
    )
    set_parent_guid_from_collection_path(
        unreal_collection.file_system_path, unreal_collection.parent_guid
    )
    set_guid_from_collection_path(
        unreal_collection.file_system_path, unreal_collection.guid
    )
    set_collection_type_from_collection_path(
        unreal_collection.file_system_path, unreal_collection.content_type
    )
    set_file_version_from_collection_path(
        unreal_collection.file_system_path, unreal_collection.file_version
    )
    set_content_lines_from_collection_path(
        unreal_collection.file_system_path, unreal_collection.content_lines
    )


# Code below is file_io specific


# def set_all_lines_in_config(config_path: str, lines: list[str]):
#     with open(config_path, 'w', encoding='utf-8') as file:
#         file.writelines(lines)


# def get_all_lines_in_config(config_path: str) -> list[str]:
#     if os.path.isfile(config_path):
#         with open(config_path, encoding='utf-8') as file:
#             return [line for line in file.readlines()]
#     else:
#         return []


def set_all_lines_in_config(
    config_path: str, lines: list[str], *, auto_add_new_line: bool = True
):
    with open(config_path, "w", encoding="utf-8") as file:
        if auto_add_new_line:
            lines = [line if line.endswith("\n") else line + "\n" for line in lines]
        file.writelines(lines)


def get_all_lines_in_config(
    config_path: str, *, auto_strip_new_lines: bool = True
) -> list[str]:
    if os.path.isfile(config_path):
        with open(config_path, encoding="utf-8") as file:
            return [
                line.rstrip("\n") if auto_strip_new_lines else line
                for line in file.readlines()
            ]
    return []


def get_files_in_dir(directory):
    return [
        f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))
    ]


def filter_by_extension(files, extension):
    return [f for f in files if f.lower().endswith(extension)]


# Code below is unreal auto mod specific


def get_unreal_collection_paths_from_mod_name(mod_name: str):
    return utilities.get_mods_info_dict_from_mod_name(mod_name)["file_includes"][
        "unreal_collections"
    ]


def add_collection_to_mod_entry(
    collection: UnrealCollection, mod_name: str, settings_json: Path
):
    settings_json_str = str(settings_json)
    try:
        collection_path = str(collection.file_system_path)

        with open(settings_json_str, encoding="utf-8") as file:
            settings = json.load(file)

        mod_entry = utilities.get_mods_info_dict_from_mod_name(mod_name)

        if mod_entry:
            new_collections = mod_entry["file_includes"]["unreal_collections"]
            if collection_path not in new_collections:
                new_collections.append(collection_path)
                mod_entry["file_includes"]["unreal_collections"] = new_collections

                for i, mod in enumerate(settings.get("mods_info", [])):
                    if mod["mod_name"] == mod_name:
                        settings["mods_info"][i] = mod_entry
                        break

                with open(settings_json_str, "w", encoding="utf-8") as file:
                    updated_json_str = json.dumps(
                        settings, indent=4, ensure_ascii=False, separators=(",", ": ")
                    )
                    file.write(updated_json_str)

                logger.log_message(
                    f"Collection added and config saved for mod '{mod_name}'."
                )
            else:
                logger.log_message(f"Collection is already added to mod '{mod_name}'.")

        else:
            logger.log_message(f"Mod entry for '{mod_name}' not found.")

    except json.JSONDecodeError:
        logger.log_message(
            f"Error decoding JSON from file '{settings_json_str}'. Please check the file format."
        )


def remove_collection_from_mod_entry(
    collection: UnrealCollection, mod_name: str, settings_json: Path
):
    settings_json_str = str(settings_json)
    collection_path = str(collection.file_system_path)

    with open(settings_json_str, encoding="utf-8") as file:
        settings = json.load(file)

    mod_entry = utilities.get_mods_info_dict_from_mod_name(mod_name)

    if mod_entry:
        new_collections = [
            other_collection_path
            for other_collection_path in mod_entry["file_includes"][
                "unreal_collections"
            ]
            if other_collection_path != collection_path
        ]
        mod_entry["file_includes"]["unreal_collections"] = new_collections

        for i, mod in enumerate(settings.get("mods_info", [])):
            if mod["mod_name"] == mod_name:
                settings["mods_info"][i] = mod_entry
                break

        with open(settings_json_str, "w", encoding="utf-8") as file:
            updated_json_str = json.dumps(
                settings, indent=4, ensure_ascii=False, separators=(",", ": ")
            )
            file.write(updated_json_str)

        logger.log_message(f"Collection removed and config saved for mod '{mod_name}'.")

    else:
        logger.log_message(f"Mod entry for '{mod_name}' not found.")


def add_collections_to_mod_entry(
    collections: list[UnrealCollection], mod_name: str, settings_json: Path
):
    for collection in collections:
        add_collection_to_mod_entry(collection, mod_name, settings_json)


def remove_collections_from_mod_entry(
    collections: list[UnrealCollection], mod_name: str, settings_json: Path
):
    for collection in collections:
        remove_collection_from_mod_entry(collection, mod_name, settings_json)
