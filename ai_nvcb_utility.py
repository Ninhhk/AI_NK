#!/usr/bin/env python3
"""
AI NVCB Utility Script

This script combines environment setup and model cleanup functionality.
Choose what you want to do from the interactive menu.
"""

import os
import sys
import shutil
import json
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Any


class AINCVBUtility:
    """Combined utility for AI NVCB environment and model management."""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.env_example_path = self.script_dir / ".env.example"
        self.env_path = self.script_dir / ".env"
    
    def show_banner(self):
        """Show application banner."""
        print("🛠️  AI NVCB Utility Tool")
        print("=" * 50)
        print("Công cụ tiện ích cho thiết lập và bảo trì hệ thống")
        print()
    
    def show_menu(self):
        """Show interactive menu."""
        print("📋 Chọn chức năng:")
        print("1. 🔧 Thiết lập môi trường (.env.example → .env)")
        print("2. 🧹 Dọn dẹp AI models không sử dụng")
        print("3. 🚀 Thực hiện cả hai (thiết lập + dọn dẹp)")
        print("4. ❌ Thoát")
        print()
        
        while True:
            try:
                choice = input("Nhập lựa chọn (1-4): ").strip()
                if choice in ['1', '2', '3', '4']:
                    return int(choice)
                else:
                    print("⚠️ Vui lòng nhập số từ 1-4")
            except KeyboardInterrupt:
                print("\n👋 Tạm biệt!")
                sys.exit(0)
    
    # ==================== ENVIRONMENT SETUP ====================
    
    def copy_env_example(self) -> bool:
        """Copy .env.example to .env file."""
        print("\n🔧 THIẾT LẬP MÔI TRƯỜNG")
        print("-" * 30)
        
        try:
            # Check if .env.example exists
            if not self.env_example_path.exists():
                print("❌ Lỗi: Không tìm thấy file .env.example!")
                print(f"   Vị trí mong đợi: {self.env_example_path}")
                return False
            
            # Check if .env already exists
            if self.env_path.exists():
                print("⚠️  Cảnh báo: File .env đã tồn tại!")
                response = input("   Bạn có muốn ghi đè không? (y/N): ").strip().lower()
                if response not in ('y', 'yes'):
                    print("   Hủy bỏ thao tác.")
                    return False
            
            # Copy the file
            shutil.copy2(self.env_example_path, self.env_path)
            
            # Verify the copy
            if self.env_path.exists():
                print("✅ Sao chép thành công .env.example → .env")
                
                # Show the content
                print("\n📄 Nội dung file .env:")
                print("-" * 40)
                with open(self.env_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(content)
                print("-" * 40)
                
                return True
            else:
                print("❌ Lỗi: Không thể tạo file .env")
                return False
                
        except PermissionError:
            print("❌ Lỗi: Không có quyền truy cập!")
            print("   Thử chạy với quyền Administrator.")
            return False
        except Exception as e:
            print(f"❌ Lỗi: {str(e)}")
            return False
    
    # ==================== MODEL CLEANUP ====================
    
    def get_current_model(self) -> str:
        """Get the current model from .env file."""
        try:
            if self.env_path.exists():
                with open(self.env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('MODEL_NAME='):
                            return line.split('=', 1)[1].strip()
            return "qwen3:8b"  # Default fallback
        except Exception:
            return "qwen3:8b"
    
    def get_ollama_models(self) -> List[Dict[str, Any]]:
        """Get list of Ollama models."""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                check=True
            )
            
            models = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        name = parts[0]
                        size = parts[2] if len(parts) > 2 else "Unknown"
                        models.append({
                            'name': name,
                            'size': size,
                            'raw_line': line
                        })
            
            return models
        except subprocess.CalledProcessError:
            print("❌ Lỗi: Không thể kết nối với Ollama")
            print("   Đảm bảo Ollama đang chạy: ollama serve")
            return []
        except FileNotFoundError:
            print("❌ Lỗi: Không tìm thấy Ollama")
            print("   Cài đặt Ollama từ: https://ollama.ai")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Download/pull a model using Ollama."""
        try:
            print(f"📥 Đang tải model: {model_name}...")
            print("   (Quá trình này có thể mất vài phút tùy thuộc vào kích thước model)")
            
            result = subprocess.run(
                ['ollama', 'pull', model_name],
                check=True,
                text=True
            )
            
            print(f"✅ Tải thành công model: {model_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Lỗi khi tải model {model_name}: {e}")
            return False
        except FileNotFoundError:
            print("❌ Lỗi: Không tìm thấy Ollama")
            print("   Cài đặt Ollama từ: https://ollama.ai")
            return False
    
    def cleanup_models(self, dry_run: bool = False, force: bool = False, keep_models: List[str] = None) -> bool:
        """Clean up unused Ollama models."""
        print("\n🧹 DỌN DẸP AI MODELS")
        print("-" * 30)
        
        if keep_models is None:
            keep_models = []
        
        # Get current model from .env
        current_model = self.get_current_model()
        print(f"📌 Model đang sử dụng: {current_model}")
          # Get all models
        models = self.get_ollama_models()
        if models is None:  # Error occurred
            return False
        
        # Check if target model exists
        current_model_exists = any(model['name'] == current_model for model in models)
        
        if not current_model_exists:
            print(f"\n⚠️  Model cần thiết không tồn tại: {current_model}")
            if dry_run:
                print("🔍 Chế độ xem trước - sẽ tải model này")
            else:
                if not force:
                    response = input(f"Bạn có muốn tải model {current_model} không? (Y/n): ").strip().lower()
                    if response in ('n', 'no'):
                        print("❌ Hủy bỏ thao tác.")
                        return False
                
                # Download the target model
                if not self.pull_model(current_model):
                    print(f"❌ Không thể tải model {current_model}")
                    return False
                  # Refresh the model list after download
                models = self.get_ollama_models()
                if not models:
                    return False
        
        if not models:
            print("\n📭 Không có model nào được cài đặt!")
            if dry_run:
                print(f"🔍 Chế độ xem trước - sẽ tải model {current_model}")
                return True
            else:
                if not force:
                    response = input(f"Bạn có muốn tải model {current_model} không? (Y/n): ").strip().lower()
                    if response in ('n', 'no'):
                        print("❌ Hủy bỏ thao tác.")
                        return False
                
                # Download the target model
                return self.pull_model(current_model)
        
        # Determine which models to keep
        models_to_keep = {current_model} | set(keep_models)
        models_to_delete = []
        
        print(f"\n📋 Tìm thấy {len(models)} model(s):")
        for model in models:
            name = model['name']
            size = model['size']
            
            if name in models_to_keep:
                status = "✅ (giữ lại)"
            else:
                status = "❌ (sẽ xóa)"
                models_to_delete.append(model)
            
            print(f"   {name} ({size}) {status}")
        
        if not models_to_delete:
            print("\n🎉 Không có model nào cần xóa!")
            return True
        
        # Show models to be deleted
        print(f"\n🗑️  Các model sẽ bị xóa ({len(models_to_delete)}):")
        total_space_estimate = 0
        for model in models_to_delete:
            print(f"   - {model['name']} ({model['size']})")
            # Rough estimate of space (very approximate)
            size_str = model['size'].lower()
            if 'gb' in size_str:
                try:
                    gb_val = float(size_str.replace('gb', '').strip())
                    total_space_estimate += gb_val
                except:
                    pass
        
        if total_space_estimate > 0:
            print(f"\n💾 Ước tính tiết kiệm: ~{total_space_estimate:.1f} GB")
        
        if dry_run:
            print("\n🔍 Chế độ xem trước - không xóa thực tế")
            return True
        
        # Confirm deletion
        if not force:
            print(f"\n⚠️  CẢNH BÁO: Thao tác này sẽ XÓA VĨNH VIỄN {len(models_to_delete)} model(s)!")
            response = input("Bạn có chắc chắn muốn tiếp tục? (y/N): ").strip().lower()
            if response not in ('y', 'yes'):
                print("Hủy bỏ thao tác.")
                return False
        
        # Delete models
        success_count = 0
        for model in models_to_delete:
            name = model['name']
            try:
                result = subprocess.run(
                    ['ollama', 'rm', name],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"✅ Đã xóa: {name}")
                success_count += 1
            except subprocess.CalledProcessError as e:
                print(f"❌ Lỗi khi xóa {name}: {e}")
        
        if success_count > 0:
            print(f"\n🎉 Dọn dẹp hoàn tất! Đã xóa {success_count}/{len(models_to_delete)} model(s)")
            if total_space_estimate > 0:
                proportion = success_count / len(models_to_delete)
                estimated_saved = total_space_estimate * proportion
                print(f"💾 Ước tính tiết kiệm: ~{estimated_saved:.1f} GB")
            return True
        else:
            print("❌ Không thể xóa model nào")
            return False
    
    # ==================== COMBINED OPERATIONS ====================
    
    def run_both(self) -> bool:
        """Run both environment setup and model cleanup."""
        print("\n🚀 THỰC HIỆN CẢ HAI CHỨC NĂNG")
        print("=" * 40)
        
        # Step 1: Environment setup
        env_success = self.copy_env_example()
        
        if env_success:
            print("\n⏱️  Chờ 2 giây trước khi dọn dẹp models...")
            import time
            time.sleep(2)
            
            # Step 2: Model cleanup
            cleanup_success = self.cleanup_models()
            
            if cleanup_success:
                print("\n🎉 Hoàn thành tất cả các thao tác!")
                return True
            else:
                print("\n⚠️  Thiết lập môi trường thành công, nhưng dọn dẹp models thất bại")
                return False
        else:
            print("\n❌ Thiết lập môi trường thất bại, bỏ qua dọn dẹp models")
            return False
    
    # ==================== MAIN INTERFACE ====================
    
    def run_interactive(self):
        """Run interactive mode."""
        self.show_banner()
        
        while True:
            choice = self.show_menu()
            
            if choice == 1:
                success = self.copy_env_example()
                if success:
                    print("\n💡 Bây giờ bạn có thể chạy ứng dụng:")
                    print("   python run_backend.py")
                    print("   python run_frontend.py")
            
            elif choice == 2:
                self.cleanup_models()
            
            elif choice == 3:
                success = self.run_both()
                if success:
                    print("\n💡 Bây giờ bạn có thể chạy ứng dụng:")
                    print("   python run_backend.py")
                    print("   python run_frontend.py")
            
            elif choice == 4:
                print("👋 Tạm biệt!")
                break
            
            # Ask if user wants to continue
            print("\n" + "─" * 50)
            continue_choice = input("Bạn có muốn thực hiện thao tác khác? (Y/n): ").strip().lower()
            if continue_choice in ('n', 'no'):
                print("👋 Tạm biệt!")
                break
            print()
    
    def run_command_line(self, args):
        """Run command line mode."""
        self.show_banner()
        
        if args.env_only:
            success = self.copy_env_example()
            if success:
                print("\n💡 Bây giờ bạn có thể chạy ứng dụng:")
                print("   python run_backend.py")
                print("   python run_frontend.py")
        
        elif args.cleanup_only:
            self.cleanup_models(
                dry_run=args.dry_run,
                force=args.force,
                keep_models=args.keep or []
            )
        
        elif args.both:
            success = self.run_both()
            if success:
                print("\n💡 Bây giờ bạn có thể chạy ứng dụng:")
                print("   python run_backend.py")
                print("   python run_frontend.py")
        
        else:
            # No specific command, run interactive
            self.run_interactive()


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI NVCB Utility - Environment setup and model cleanup tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python ai_nvcb_utility.py                    # Chế độ tương tác
  python ai_nvcb_utility.py --env-only         # Chỉ thiết lập môi trường
  python ai_nvcb_utility.py --cleanup-only     # Chỉ dọn dẹp models
  python ai_nvcb_utility.py --both             # Cả hai chức năng
  python ai_nvcb_utility.py --cleanup-only --dry-run    # Xem trước không xóa
  python ai_nvcb_utility.py --cleanup-only --keep mistral:7b  # Giữ lại model cụ thể
        """
    )
    
    # Main actions
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--env-only',
        action='store_true',
        help='Chỉ thiết lập môi trường (.env.example → .env)'
    )
    group.add_argument(
        '--cleanup-only',
        action='store_true',
        help='Chỉ dọn dẹp AI models không sử dụng'
    )
    group.add_argument(
        '--both',
        action='store_true',
        help='Thực hiện cả thiết lập môi trường và dọn dẹp models'
    )
    
    # Cleanup options
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Xem trước models sẽ bị xóa (không xóa thực tế)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Bỏ qua xác nhận (cẩn thận!)'
    )
    parser.add_argument(
        '--keep',
        action='append',
        help='Giữ lại model cụ thể (có thể dùng nhiều lần)'
    )
    
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()
    utility = AINCVBUtility()
    
    try:
        utility.run_command_line(args)
    except KeyboardInterrupt:
        print("\n👋 Tạm biệt!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Lỗi không mong đợi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
