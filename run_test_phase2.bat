@echo off
cd /d "c:\Users\George Guo\WorkBuddy\20260422151119"
"C:\Users\George Guo\.workbuddy\binaries\python\versions\3.13.12\python.exe" -c "import sys; sys.path.insert(0, '.'); from TalentAI_Pro.tests.test_phase2 import main; success = main(); sys.exit(0 if success else 1)"