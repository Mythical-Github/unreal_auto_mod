from pathlib import Path


def add_meta_data_tags_for_asset_registry_to_unreal_ini(ini: Path, tags: list[str]):
    with ini.open("r") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith("MetaDataTagsForAssetRegistry"):
            existing_tags = (
                line.split("=")[1].strip().strip("()").replace('"', "").split(",")
            )
            existing_tags = [tag.strip() for tag in existing_tags if tag.strip()]

            for tag in tags:
                if tag not in existing_tags:
                    existing_tags.append(tag)

            updated_tags = ",".join(f'"{tag}"' for tag in existing_tags)
            lines[i] = f"MetaDataTagsForAssetRegistry=({updated_tags})\n"
            break
    else:
        updated_tags = ",".join(f'"{tag}"' for tag in tags)
        lines.append(f"MetaDataTagsForAssetRegistry=({updated_tags})\n")

    with ini.open("w") as file:
        file.writelines(lines)


def remove_meta_data_tags_for_asset_registry_from_unreal_ini(
    ini: Path, tags: list[str]
):
    with ini.open("r") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith("MetaDataTagsForAssetRegistry"):
            existing_tags = (
                line.split("=")[1].strip().strip("()").replace('"', "").split(",")
            )
            existing_tags = [tag.strip() for tag in existing_tags if tag.strip()]

            updated_tags = [tag for tag in existing_tags if tag not in tags]

            if updated_tags:
                updated_tags = ",".join(f'"{tag}"' for tag in updated_tags)
                lines[i] = f"MetaDataTagsForAssetRegistry=({updated_tags})\n"
            else:
                lines[i] = "MetaDataTagsForAssetRegistry=()\n"
            break
    else:
        return

    with ini.open("w") as file:
        file.writelines(lines)


# def disable_serialized_properties_in_ini():
#     return


# def enable_serialized_properties_in_ini():
#     return


# def set_default_map_in_ini():
#     return


# def get_default_map_in_ini():
#     return


# def disable_share_material_libraries():
#     return


# def disable_share_material_code():
#     return


# def disable_iostore():
#     return


# def disable_chunking():
#     return


# def set_unreal_engine_theme():
#     return


# def delete_asset_manager_maps_rule():
#     return


# def enable_iterative_cooking():
#     return


# def enable_compressed_paks():
#     return


# def enable_using_pak():
#     return


# def set_default_editor_startup_map():
#     return


# def set_editor_splash_screen():
#     return


# def add_layout():
#     return


# def remove_layout():
#     return


# def set_default_layout():
#     return


# def enable_plugin_in_uproject():
#     return


# def disable_uplugin_in_uproject():
#     return


# gameplay tag stuff, collision stuff
