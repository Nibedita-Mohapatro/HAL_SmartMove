#!/usr/bin/env python3
"""
HAL SmartMove - Project Cleanup Script

This script safely removes unnecessary files and folders from the HAL SmartMove
project directory to create a lean, production-ready codebase.

Usage:
    python cleanup_project.py --preview    # Show what will be deleted
    python cleanup_project.py --execute    # Actually delete the files
"""

import os
import shutil
import argparse
from pathlib import Path

class ProjectCleaner:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.deleted_files = []
        self.deleted_dirs = []
        self.errors = []

    def get_files_to_delete(self):
        """Return list of files and directories to delete"""
        files_to_delete = [
            # Duplicate/Redundant Documentation
            "ADMIN_DASHBOARD_FIX_REPORT.md",
            "ADMIN_FIXES_SUMMARY.md",
            "APPROVE_ASSIGN_BUTTON_REMOVAL_SUMMARY.md",
            "BRANDING_UPDATE_SUMMARY.md",
            "DEPLOYMENT_CHECKLIST.md",
            "DEPLOYMENT_READY_SUMMARY.md",
            "DRIVER_DELETION_FIX_SUMMARY.md",
            "GITHUB_UPLOAD_GUIDE.md",
            "INSTALLATION.md",
            "LAUNCHER_README.md",
            "PRODUCTION_DEPLOYMENT.md",
            "SYSTEM_STATUS_REPORT.md",
            "UI_ELEMENTS_REMOVAL_SUMMARY.md",
            
            # Temporary/Cache Files
            "backend/app.log",
            "backend/hal_transport.db",  # Keep hal_transport_system.db
            
            # Test/Development Scripts (Outdated)
            "backend/assign_trip_to_hal002.py",
            "backend/check_database.py",
            "backend/check_transport_users.py",
            "backend/create_transport_driver.py",
            "backend/test_admin_workflow.py",
            "backend/test_login.py",
            "backend/test_transport_api.py",
            "backend/test_transport_requests.py",
            "comprehensive_cleanup_optimization.py",
            "create_transport_driver_profile.py",
            "final_comprehensive_validation.py",
            "final_system_report.py",
            "sample_data.py",
            "test_admin_functionalities.py",
            "test_cancel_functionality.py",
            "test_driver_deletion.py",  # Root level (keep backend version)
            "test_user_deletion.py",
            
            # Redundant Startup Scripts
            "launcher.bat",
            "launcher.sh",
            "deploy.sh",
            "setup.sh",
            "Makefile",
            
            # Unused Backend Files
            "backend/gps_tracking.py",
            "backend/ml_algorithms.py",
        ]
        
        dirs_to_delete = [
            # Cache Directories
            "backend/__pycache__",
            "backend/app/__pycache__",
            
            # Redundant Documentation
            "docs",
            "database",
            
            # Empty uploads directory (check if empty first)
            "backend/uploads",
        ]
        
        return files_to_delete, dirs_to_delete

    def check_if_empty_dir(self, dir_path):
        """Check if directory is empty"""
        try:
            return len(list(dir_path.iterdir())) == 0
        except:
            return False

    def preview_cleanup(self):
        """Show what will be deleted without actually deleting"""
        print("🔍 HAL SmartMove Project Cleanup Preview")
        print("=" * 50)
        
        files_to_delete, dirs_to_delete = self.get_files_to_delete()
        
        print("\n📄 FILES TO BE DELETED:")
        print("-" * 30)
        total_files = 0
        total_size = 0
        
        for file_path in files_to_delete:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    size = full_path.stat().st_size
                    total_size += size
                    total_files += 1
                    print(f"❌ {file_path} ({size:,} bytes)")
                except:
                    print(f"❌ {file_path} (size unknown)")
            else:
                print(f"⚠️  {file_path} (not found)")
        
        print(f"\n📁 DIRECTORIES TO BE DELETED:")
        print("-" * 30)
        total_dirs = 0
        
        for dir_path in dirs_to_delete:
            full_path = self.project_root / dir_path
            if full_path.exists():
                if dir_path == "backend/uploads" and not self.check_if_empty_dir(full_path):
                    print(f"⚠️  {dir_path} (not empty - will be skipped)")
                else:
                    total_dirs += 1
                    try:
                        # Count files in directory
                        file_count = sum(1 for _ in full_path.rglob('*') if _.is_file())
                        print(f"❌ {dir_path} ({file_count} files)")
                    except:
                        print(f"❌ {dir_path}")
            else:
                print(f"⚠️  {dir_path} (not found)")
        
        print(f"\n📊 CLEANUP SUMMARY:")
        print("-" * 30)
        print(f"Files to delete: {total_files}")
        print(f"Directories to delete: {total_dirs}")
        print(f"Total size to free: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
        
        print(f"\n✅ ESSENTIAL FILES PRESERVED:")
        print("-" * 30)
        essential_files = [
            "README.md", "SETUP.md", "DEPLOYMENT.md", "ARCHITECTURE.md",
            "USER_GUIDE.md", "TROUBLESHOOTING.md", "SYSTEM_STATE.md",
            "start_system.py", "health_check.py", "run_app.py",
            "backend/main.py", "backend/requirements.txt",
            "backend/hal_transport_system.db", "frontend/package.json"
        ]
        
        for file_path in essential_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"✅ {file_path}")
            else:
                print(f"⚠️  {file_path} (missing!)")

    def execute_cleanup(self):
        """Actually delete the files and directories"""
        print("🧹 Executing HAL SmartMove Project Cleanup")
        print("=" * 50)
        
        files_to_delete, dirs_to_delete = self.get_files_to_delete()
        
        # Delete files
        print("\n📄 Deleting files...")
        for file_path in files_to_delete:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    full_path.unlink()
                    self.deleted_files.append(file_path)
                    print(f"✅ Deleted: {file_path}")
                except Exception as e:
                    self.errors.append(f"Failed to delete {file_path}: {e}")
                    print(f"❌ Failed: {file_path} - {e}")
            else:
                print(f"⚠️  Not found: {file_path}")
        
        # Delete directories
        print("\n📁 Deleting directories...")
        for dir_path in dirs_to_delete:
            full_path = self.project_root / dir_path
            if full_path.exists():
                # Special handling for uploads directory
                if dir_path == "backend/uploads" and not self.check_if_empty_dir(full_path):
                    print(f"⚠️  Skipped: {dir_path} (not empty)")
                    continue
                
                try:
                    shutil.rmtree(full_path)
                    self.deleted_dirs.append(dir_path)
                    print(f"✅ Deleted: {dir_path}")
                except Exception as e:
                    self.errors.append(f"Failed to delete {dir_path}: {e}")
                    print(f"❌ Failed: {dir_path} - {e}")
            else:
                print(f"⚠️  Not found: {dir_path}")
        
        # Summary
        print(f"\n📊 CLEANUP RESULTS:")
        print("-" * 30)
        print(f"Files deleted: {len(self.deleted_files)}")
        print(f"Directories deleted: {len(self.deleted_dirs)}")
        print(f"Errors: {len(self.errors)}")
        
        if self.errors:
            print(f"\n❌ ERRORS:")
            for error in self.errors:
                print(f"   {error}")
        
        print(f"\n✅ Cleanup completed!")
        print(f"💡 Run 'python run_app.py' to verify the system still works")

def main():
    parser = argparse.ArgumentParser(description="HAL SmartMove Project Cleanup")
    parser.add_argument("--preview", action="store_true", help="Preview what will be deleted")
    parser.add_argument("--execute", action="store_true", help="Execute the cleanup")
    
    args = parser.parse_args()
    
    if not args.preview and not args.execute:
        print("❌ Please specify either --preview or --execute")
        parser.print_help()
        return
    
    # Get current directory (should be project root)
    project_root = Path.cwd()
    
    # Verify we're in the right directory
    if not (project_root / "backend").exists() or not (project_root / "frontend").exists():
        print("❌ Error: This doesn't appear to be the HAL SmartMove project root directory")
        print(f"Current directory: {project_root}")
        print("Please run this script from the project root directory")
        return
    
    cleaner = ProjectCleaner(project_root)
    
    if args.preview:
        cleaner.preview_cleanup()
        print(f"\n💡 To execute cleanup, run: python cleanup_project.py --execute")
    
    if args.execute:
        confirm = input("\n⚠️  Are you sure you want to delete these files? (yes/no): ")
        if confirm.lower() == 'yes':
            cleaner.execute_cleanup()
        else:
            print("❌ Cleanup cancelled")

if __name__ == "__main__":
    main()
