"""
FFmpeg Diagnostic Tool for Windows
Run this script to diagnose ffmpeg/pydub issues
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_file_exists(filepath):
    """Check if file exists and is accessible"""
    exists = os.path.exists(filepath)
    if exists:
        size = os.path.getsize(filepath)
        print(f"  [OK] Found: {filepath} ({size:,} bytes)")
        return True
    else:
        print(f"  [FAIL] Not found: {filepath}")
        return False


def test_executable(exe_path, test_args=["-version"]):
    """Test if an executable can be run"""
    try:
        result = subprocess.run(
            [exe_path] + test_args,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"  [OK] Executable works: {version}")
            return True
        else:
            print(f"  [FAIL] Executable failed with code {result.returncode}")
            print(f"    stderr: {result.stderr[:200]}")
            return False
    except FileNotFoundError:
        print(f"  [FAIL] FileNotFoundError when trying to execute")
        return False
    except Exception as e:
        print(f"  [FAIL] Error: {type(e).__name__}: {e}")
        return False


def check_dll_dependencies(exe_path):
    """Check if DLL dependencies are available"""
    exe_dir = os.path.dirname(exe_path)
    common_dlls = [
        "avcodec-*.dll", "avformat-*.dll", "avutil-*.dll",
        "swresample-*.dll", "swscale-*.dll"
    ]
    
    print(f"\n  Checking for DLLs in: {exe_dir}")
    import glob
    found_dlls = []
    for pattern in common_dlls:
        matches = glob.glob(os.path.join(exe_dir, pattern))
        if matches:
            for dll in matches:
                found_dlls.append(os.path.basename(dll))
    
    if found_dlls:
        print(f"  [OK] Found {len(found_dlls)} DLL(s): {', '.join(found_dlls[:3])}")
        return True
    else:
        print(f"  [FAIL] No FFmpeg DLLs found - this may cause issues")
        return False


def test_pydub_import():
    """Test pydub import and configuration"""
    try:
        import pydub
        from pydub import AudioSegment
        print(f"  [OK] pydub imported successfully (version: {pydub.__version__})")
        
        # Check current configuration
        converter = getattr(AudioSegment, 'converter', None)
        ffprobe = getattr(AudioSegment, 'ffprobe', None)
        
        print(f"  Current converter: {converter}")
        print(f"  Current ffprobe: {ffprobe}")
        
        return True
    except ImportError as e:
        print(f"  [FAIL] pydub import failed: {e}")
        return False


def test_conversion(ffmpeg_path, test_audio_path=None):
    """Test actual audio conversion"""
    if not test_audio_path:
        print("\n  Skipping conversion test (no test audio provided)")
        return None
    
    if not os.path.exists(test_audio_path):
        print(f"\n  Test audio not found: {test_audio_path}")
        return None
    
    output_path = "test_output.wav"
    
    try:
        print(f"\n  Testing conversion: {test_audio_path} -> {output_path}")
        result = subprocess.run(
            [
                ffmpeg_path,
                "-i", test_audio_path,
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                "-y",  # Overwrite output
                output_path
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"  [OK] Conversion successful ({size:,} bytes)")
            os.remove(output_path)
            return True
        else:
            print(f"  [FAIL] Conversion failed")
            print(f"    stderr: {result.stderr[:300]}")
            return False
            
    except Exception as e:
        print(f"  [FAIL] Conversion error: {e}")
        return False


def main():
    print("=" * 70)
    print("FFmpeg Diagnostic Tool for Windows")
    print("=" * 70)
    
    # System info
    print(f"\n1. SYSTEM INFORMATION")
    print(f"  Platform: {platform.system()} {platform.release()}")
    print(f"  Python: {sys.version.split()[0]} ({sys.executable})")
    
    # Check conda environment
    print(f"\n2. CONDA ENVIRONMENT")
    conda_root = r"C:\Users\ahmed\anaconda3"
    conda_bin = os.path.join(conda_root, "Library", "bin")
    
    if os.path.exists(conda_root):
        print(f"  [OK] Conda root found: {conda_root}")
    else:
        print(f"  [FAIL] Conda root not found: {conda_root}")
    
    if os.path.exists(conda_bin):
        print(f"  [OK] Conda bin found: {conda_bin}")
    else:
        print(f"  [FAIL] Conda bin not found: {conda_bin}")
    
    # Check PATH
    print(f"\n3. PATH ENVIRONMENT")
    current_path = os.environ.get('PATH', '')
    path_entries = current_path.split(os.pathsep)
    
    if conda_bin in path_entries:
        print(f"  [OK] Conda bin is in PATH")
    else:
        print(f"  [WARNING] Conda bin NOT in PATH (will be added dynamically)")
    
    print(f"  Total PATH entries: {len(path_entries)}")
    
    # Check ffmpeg files
    print(f"\n4. FFMPEG EXECUTABLES")
    ffmpeg_path = os.path.join(conda_bin, "ffmpeg.exe")
    ffprobe_path = os.path.join(conda_bin, "ffprobe.exe")
    
    ffmpeg_exists = check_file_exists(ffmpeg_path)
    ffprobe_exists = check_file_exists(ffprobe_path)
    
    # Check DLL dependencies
    print(f"\n5. DLL DEPENDENCIES")
    if ffmpeg_exists:
        check_dll_dependencies(ffmpeg_path)
    
    # Test executables
    print(f"\n6. EXECUTABLE TESTS")
    if ffmpeg_exists:
        print(f"  Testing ffmpeg.exe:")
        ffmpeg_works = test_executable(ffmpeg_path)
    else:
        ffmpeg_works = False
    
    if ffprobe_exists:
        print(f"\n  Testing ffprobe.exe:")
        ffprobe_works = test_executable(ffprobe_path)
    else:
        ffprobe_works = False
    
    # Test pydub
    print(f"\n7. PYDUB CONFIGURATION")
    pydub_ok = test_pydub_import()
    
    # Test pydub with ffmpeg
    if pydub_ok and ffmpeg_works:
        print(f"\n8. PYDUB + FFMPEG INTEGRATION TEST")
        try:
            from pydub import AudioSegment
            
            # Configure pydub
            AudioSegment.converter = ffmpeg_path
            AudioSegment.ffprobe = ffprobe_path
            os.environ['PATH'] = conda_bin + os.pathsep + os.environ.get('PATH', '')
            
            print(f"  [OK] Configured pydub with ffmpeg")
            print(f"    converter: {AudioSegment.converter}")
            print(f"    ffprobe: {AudioSegment.ffprobe}")
            
        except Exception as e:
            print(f"  [FAIL] Configuration failed: {e}")
    
    # Summary
    print(f"\n" + "=" * 70)
    print(f"DIAGNOSTIC SUMMARY")
    print(f"=" * 70)
    
    all_checks = [
        ("FFmpeg exists", ffmpeg_exists),
        ("FFprobe exists", ffprobe_exists),
        ("FFmpeg executable works", ffmpeg_works if ffmpeg_exists else False),
        ("Pydub imports", pydub_ok)
    ]
    
    passed = sum(1 for _, result in all_checks if result)
    total = len(all_checks)
    
    for check_name, result in all_checks:
        status = "[OK]" if result else "[FAIL]"
        print(f"  {status}: {check_name}")
    
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n[OK] All checks passed! Your setup should work.")
    else:
        print("\n[FAIL] Some checks failed. See details above.")
        print("\nRECOMMENDED ACTIONS:")
        if not ffmpeg_exists:
            print("  - Install ffmpeg: conda install ffmpeg")
        if ffmpeg_exists and not ffmpeg_works:
            print("  - Reinstall ffmpeg: conda install -c conda-forge ffmpeg --force-reinstall")
        if not pydub_ok:
            print("  - Install pydub: pip install pydub")


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")