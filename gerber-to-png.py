import argparse
import logging
import os
import pathlib
import subprocess


def list_gerber_files(gerber_path):
    gerber_extensions = [
        ".gbl",
        ".gbs",
        ".gbp",
        ".gbo",
        ".gbr",
        ".gm1",
        ".gtl",
        ".gts",
        ".gtp",
        ".gto",
        ".g2",
        ".g3",
        ".g4",
        ".g5",
        ".drl",
    ]
    gerber_files = [
        f for f in gerber_path.iterdir() if f.is_file() if f.suffix in gerber_extensions
    ]
    return gerber_files


def init_parser():
    parser = argparse.ArgumentParser(description="Convert Gerber file to PNG")
    parser.add_argument(
        "paths",
        metavar="paths",
        type=pathlib.Path,
        help="path of Gerber files folder",
        nargs="+",
    )
    parser.add_argument(
        "--output_type",
        dest="type",
        type=ascii,
        default="png",
        help="output file format (default: png)",
    )
    return parser


def create_output_folder(folder_name):
    try:
        os.mkdir(folder_name)
    except FileExistsError:
        logging.error(f"Directory {folder_name} already exists")
    except OSError:
        logging.error(f"Creation of the directory failed {folder_name}")
    else:
        logging.info(f"Successfully created the directory {folder_name}")
    finally:
        return pathlib.Path.cwd().joinpath(folder_name)


def gerber_to_png(path, output_type):
    folder_name = str(path.name)
    for path in list_gerber_files(path):
        logging.debug(f"Converting Gerber file {path} to PNG")
        name = str(path.name)
        path = str(path)

        gerbv_converter = subprocess.run(
            [
                "gerbv",
                f"--export={type}",
                "-o",
                f"{folder_name}/{name}.png",
                "--dpi=1000",
                #"--window=5709x1576",
                f"{path}",
            ],
            check=True,
        )


def compare_pngs(png1_path, png2_path, diff_path):
    imagemagick_composite = subprocess.run(
        [
            "composite",
            "-stereo",
            "0",
            f"{png1_path}",
            f"{png2_path}",
            f"{diff_path}",
        ],
        check=False,
    )


def compare_png_folders(folder1_path, folder2_path, diff_folder_path):
    image_files_folder1 = [f for f in folder1_path.iterdir() if f.is_file()]
    image_files_folder1.sort()
    image_files_folder2 = [f for f in folder2_path.iterdir() if f.is_file()]
    image_files_folder2.sort()
    diff_folder_path = create_output_folder(diff_folder_path)
    for (file1, file2) in zip(image_files_folder1, image_files_folder2):
        if file1.name == file2.name:
            logging.info(f"Comparing {file1} and {file2}")
            compare_pngs(
                file1, file2, diff_folder_path.joinpath(f"{file1.stem}_diff.png")
            )
        else:
            logging.error(f"File names do not match: {file1} != {file2}")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        level=logging.INFO,
    )
    parser = init_parser()
    args = parser.parse_args()
    type = str(args.type).strip("'")
    paths = args.paths

    output_folders = []
    for path in paths:
        folder_name = str(path.name)
        output_folders.append(create_output_folder(folder_name))
        gerber_to_png(path, type)

    compare_png_folders(
        output_folders[0], output_folders[1], f"{paths[0].name}_{paths[1].name}_diff"
    )
