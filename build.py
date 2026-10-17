#!/usr/bin/env python3
"""Compila a biblioteca Tainah e executa seu teste de ABI."""
import argparse
import os
import pathlib
import shutil
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parent
REVISION = "9acdea90da8bb7eb8b2e83f302070364fd838a10"
ENGINE_URL = "https://github.com/dorayakito/lessampler-ng.git"


def run(command, **kwargs):
    subprocess.run(command, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=pathlib.Path, help="diretório para os artefatos finais")
    args = parser.parse_args()

    work = ROOT / "build"
    supplied_source = os.environ.get("TAINAH_ENGINE_SOURCE")
    engine = work / "engine-source"
    build = work / "engine-build"
    package = args.output.resolve() if args.output else work / "package"

    if not engine.exists():
        engine.parent.mkdir(parents=True, exist_ok=True)
        clone_url = str(pathlib.Path(supplied_source).resolve()) if supplied_source else ENGINE_URL
        run(["git", "clone", "--no-checkout", clone_url, str(engine)])
        run(["git", "checkout", REVISION], cwd=engine)
        run(["git", "submodule", "update", "--init", "--recursive"], cwd=engine)
    else:
        current = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=engine, text=True
        ).strip()
        if current != REVISION:
            raise SystemExit(
                f"revisão da base de síntese incompatível: {current}; esperada: {REVISION}"
            )
        run(["git", "submodule", "update", "--init", "--recursive"], cwd=engine)

    destination = engine / "src" / "Tainah"
    destination.mkdir(exist_ok=True)
    for name in ("tainah.h", "tainah.cpp", "tainah_abi_test.cpp", "CMakeLists.txt"):
        shutil.copy2(ROOT / "src" / "Tainah" / name, destination / name)
    shutil.copy2(ROOT / "patches" / "lessConfigure.h", engine / "src" / "ConfigUnit" / "lessConfigure.h")
    shutil.copy2(
        ROOT / "patches" / "WorldModule.cpp",
        engine / "src" / "AudioModel" / "WorldModule" / "WorldModule.cpp",
    )

    cmake_file = engine / "CMakeLists.txt"
    cmake_text = cmake_file.read_text(encoding="utf-8")
    if "enable_testing()" not in cmake_text:
        cmake_text = cmake_text.replace(
            "add_subdirectory(src)\n", "enable_testing()\nadd_subdirectory(src)\n"
        )
    if "add_subdirectory(src/Tainah)" not in cmake_text:
        cmake_text = cmake_text.replace(
            "add_subdirectory(src)\n",
            "add_subdirectory(src)\nadd_subdirectory(src/Tainah)\n",
        )
    cmake_file.write_text(cmake_text, encoding="utf-8")

    configure = [
        "cmake", "-S", str(engine), "-B", str(build),
        "-DBUILD_TESTING=ON", "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
    ]
    if sys.platform == "win32":
        configure += ["-A", os.environ.get("TAINAH_WINDOWS_ARCH", "x64")]
    run(configure)
    run([
        "cmake", "--build", str(build), "--config", "Release",
        "--target", "lessampler_tainah", "lessampler_tainah_abi_test", "--parallel", "4",
    ])
    listing = subprocess.check_output(
        ["ctest", "--test-dir", str(build), "-N", "-R", "tainah_abi"], text=True
    )
    if "tainah_abi" not in listing:
        raise SystemExit("o teste de ABI não foi registrado no CTest")
    run([
        "ctest", "--test-dir", str(build), "-C", "Release",
        "-R", "tainah_abi", "--output-on-failure",
    ])

    libraries = (
        list(build.rglob("lessampler_tainah.dll"))
        + list(build.rglob("liblessampler_tainah.dylib"))
        + list(build.rglob("liblessampler_tainah.so.1"))
    )
    if len(libraries) != 1:
        raise SystemExit(f"era esperada uma biblioteca; encontradas: {libraries}")
    package.mkdir(parents=True, exist_ok=True)
    shutil.copy2(libraries[0], package / libraries[0].name)
    shutil.copy2(engine / "LICENSE", package / "licenca-da-base-LGPL-3.0.txt")
    print(package)


if __name__ == "__main__":
    main()
