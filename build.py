#!/usr/bin/env python3
"""Compila a biblioteca Tainah e executa seu teste de ABI."""
import argparse
import math
import os
import pathlib
import shutil
import struct
import subprocess
import sys
import wave


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
    for name in ("tainah.h", "tainah.cpp", "tainah_cli.cpp", "tainah_abi_test.cpp", "CMakeLists.txt"):
        shutil.copy2(ROOT / "src" / "Tainah" / name, destination / name)
    shutil.copy2(ROOT / "patches" / "TainahConfig.h", engine / "src" / "ConfigUnit" / "lessConfigure.h")
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
        "--target", "tainah_motor", "Tainah", "tainah_abi_test", "--parallel", "4",
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
        list(build.rglob("tainah_motor.dll"))
        + list(build.rglob("libtainah_motor.dylib"))
        + list(build.rglob("libtainah_motor.so.1"))
    )
    if len(libraries) != 1:
        raise SystemExit(f"era esperada uma biblioteca; encontradas: {libraries}")
    package.mkdir(parents=True, exist_ok=True)
    shutil.copy2(libraries[0], package / libraries[0].name)
    if sys.platform == "darwin":
        shutil.copy2(libraries[0], package / "libtainah_motor.1.dylib")
    executables = list(build.rglob("Tainah.exe")) if sys.platform == "win32" else list(build.rglob("Tainah"))
    executables = [path for path in executables if path.is_file() and "CMakeFiles" not in path.parts]
    if len(executables) != 1:
        raise SystemExit(f"era esperado um executável Tainah; encontrados: {executables}")
    shutil.copy2(executables[0], package / executables[0].name)
    shutil.copy2(engine / "LICENSE", package / "licenca-da-base-LGPL-3.0.txt")
    shutil.copy2(ROOT / "LICENSE", package / "LICENSE")
    shutil.copy2(ROOT / "NOTICE.md", package / "NOTICE.md")
    shutil.copy2(ROOT / "src" / "Tainah" / "Tainah.yaml", package / "Tainah.yaml")
    test_dir = work / "cli-smoke-test"
    test_dir.mkdir(parents=True, exist_ok=True)
    input_wav = test_dir / "entrada.wav"
    output_wav = test_dir / "saida.wav"
    rate = 44100
    with wave.open(str(input_wav), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        samples = (int(10000 * (math.sin(2 * math.pi * 220 * i / rate) + 0.2 * math.sin(2 * math.pi * 440 * i / rate))) for i in range(rate))
        wav.writeframes(b"".join(struct.pack("<h", sample) for sample in samples))
    executable = package / ("Tainah.exe" if sys.platform == "win32" else "Tainah")
    run([str(executable), str(input_wav), str(output_wav), "A3", "100", "g0B0H0",
         "0", "250", "50", "0", "100", "0", "!120", "AABk#48#"])
    with wave.open(str(output_wav), "rb") as wav:
        samples = wav.readframes(wav.getnframes())
        if wav.getnchannels() != 1 or wav.getframerate() != rate or wav.getnframes() != 11025:
            raise SystemExit("o teste do executável produziu taxa ou duração inesperada")
        if not samples or max(abs(value[0]) for value in struct.iter_unpack("<h", samples)) < 1:
            raise SystemExit("o teste do executável produziu áudio silencioso")
    print("Executável testado: WAV mono, 44,1 kHz, 250 ms e áudio presente.")
    print(package)


if __name__ == "__main__":
    main()
