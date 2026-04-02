import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
from pathlib import Path
import json

from TextAnalyst import TextAnalyzer


class TextAnalyzerGUI:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("Анализатор текста")
        self.root.geometry("1200x700")

        self.setup_styles()

        self.analyzer = None
        self.current_file = None

        self.setup_ui()


    def setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        style.theme_use('clam')

        self.root.configure(bg='#f5f5f5')

        style.configure('Accent.TButton', background='#4CAF50', foreground='white')
        style.map('Accent.TButton',
                  background=[('active', '#45a049'), ('pressed', '#3d8b40')])


    def setup_ui(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill='x', pady=(0, 10))

        self.select_btn = ttk.Button(button_frame, text="📂 Выбрать файл", command=self.select_file, style='Accent.TButton')
        self.select_btn.pack(side='left', padx=5)
        self.analyze_btn = ttk.Button(button_frame, text="🔍 Выполнить анализ", command=self.analyze_text, state='disabled')
        self.analyze_btn.pack(side='left', padx=5)
        self.save_btn = ttk.Button(button_frame, text="💾 Сохранить в JSON", command=self.save_to_json, state='disabled')
        self.save_btn.pack(side='left', padx=5)
        self.clear_btn = ttk.Button(button_frame, text="🗑️ Очистить", command=self.clear_all)
        self.clear_btn.pack(side='left', padx=5)

        paned = ttk.PanedWindow(main_container, orient='horizontal')
        paned.pack(fill='both', expand=True)

        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        drop_frame = ttk.LabelFrame(left_frame, text="Drag & Drop", padding=10)
        drop_frame.pack(fill='x', pady=(0, 10))

        self.drop_label = tk.Label(drop_frame,
                                   text=" Перетащите текстовый файл сюда \n\n или нажмите кнопку 'Выбрать файл'",
                                   justify='center',
                                   bg='#f8f9fa',
                                   relief='groove',
                                   height=8,
                                   font=('Arial', 10))
        self.drop_label.pack(fill='both', expand=True)

        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.on_drop)
        self.drop_label.dnd_bind('<<DragEnter>>', self.on_drag_enter)
        self.drop_label.dnd_bind('<<DragLeave>>', self.on_drag_leave)

        info_frame = ttk.LabelFrame(left_frame, text="Информация о файле", padding=5)
        info_frame.pack(fill='x', pady=(0, 10))

        self.file_info = tk.Text(info_frame, height=8, width=30, wrap='word', bg='#f8f9fa', font=('Courier', 9))
        self.file_info.pack(fill='both', expand=True, padx=5, pady=5)
        self.file_info.config(state='disabled')

        filters_frame = ttk.LabelFrame(left_frame, text="Фильтры анализа", padding=5)
        filters_frame.pack(fill='x')

        self.filter_var = tk.StringVar(value="all")
        ttk.Radiobutton(filters_frame, text="Все категории", variable=self.filter_var, value="all").pack(anchor='w', padx=5, pady=2)
        ttk.Radiobutton(filters_frame, text="Только буквы", variable=self.filter_var, value="letters").pack(anchor='w', padx=5, pady=2)
        ttk.Radiobutton(filters_frame, text="Только слова", variable=self.filter_var, value="words").pack(anchor='w', padx=5, pady=2)

        right_notebook = ttk.Notebook(paned)
        paned.add(right_notebook, weight=3)

        results_frame = ttk.Frame(right_notebook)
        right_notebook.add(results_frame, text="📊 Результаты анализа")

        self.results_tree = ttk.Treeview(results_frame, columns=('value',), show='tree headings')
        self.results_tree.heading('#0', text='Параметр')
        self.results_tree.heading('value', text='Значение')
        self.results_tree.column('#0', width=250)
        self.results_tree.column('value', width=400)
        tree_scroll = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=tree_scroll.set)
        self.results_tree.pack(side='left', fill='both', expand=True)
        tree_scroll.pack(side='right', fill='y')

        text_frame = ttk.Frame(right_notebook)
        right_notebook.add(text_frame, text="📄 Содержимое файла")

        self.text_display = scrolledtext.ScrolledText(text_frame, wrap='word', font=('Courier', 10))
        self.text_display.pack(fill='both', expand=True)

        self.status_bar = ttk.Label(self.root, text="Готов к работе. Перетащите файл или выберите его.", relief='sunken', anchor='w')
        self.status_bar.pack(side='bottom', fill='x')


    def on_drop(self, event):
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        self.load_file(file_path)
        self.drop_label.config(bg='#f8f9fa')
        return 'break'


    def on_drag_enter(self, event):
        self.drop_label.config(bg='#e8f5e9', text="📂 Отпустите файл для загрузки")
        return 'break'


    def on_drag_leave(self, event):
        self.drop_label.config(bg='#f8f9fa', text="📁 Перетащите текстовый файл сюда\n\nили нажмите кнопку 'Выбрать файл'")
        return 'break'


    def get_active_filters(self):
        filter_value = self.filter_var.get()
        if filter_value == "all":
            return None
        elif filter_value == "letters":
            return ["letters"]
        elif filter_value == "words":
            return ["words"]
        return None


    def load_file(self, file_path):
        try:
            self.current_file = file_path
            self.analyzer = TextAnalyzer(file_path)

            self.file_info.config(state='normal')
            self.file_info.delete(1.0, tk.END)

            try:
                words = self.analyzer._get_words()
                words_count = len(words)
            except:
                words_count = 0

            file_info_text = f"""📄 Имя файла: {Path(file_path).name}
📁 Путь: {file_path}
📊 Размер: {os.path.getsize(file_path):,} байт
📝 Символов: {len(self.analyzer.text):,}
🔤 Слов: {words_count:,}"""
            self.file_info.insert(1.0, file_info_text)
            self.file_info.config(state='disabled')

            self.text_display.delete(1.0, tk.END)
            preview_text = self.analyzer.text[:5000]
            self.text_display.insert(1.0, preview_text)

            if len(self.analyzer.text) > 5000:
                self.text_display.insert(tk.END,
                                         f"\n\n... (показано только первые 5000 символов из {len(self.analyzer.text)})")

            self.analyze_btn.config(state='normal')
            self.save_btn.config(state='disabled')
            self.update_status(f"Файл загружен: {Path(file_path).name}")

        except FileNotFoundError:
            messagebox.showerror("Ошибка", f"Файл не найден:\n{file_path}")
            self.update_status("Ошибка: файл не найден")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
            self.update_status("Ошибка загрузки файла")


    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите текстовый файл",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if file_path:
            self.load_file(file_path)


    def analyze_text(self):
        if not self.analyzer:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл")
            return

        try:
            filters = self.get_active_filters()
            self.update_status("Выполняется анализ текста...")
            self.root.update()

            stats = self.analyzer.analyze(filters=filters)

            self.display_results(stats)

            self.save_btn.config(state='normal')
            self.update_status("Анализ завершен")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при анализе текста:\n{str(e)}")
            self.update_status("Ошибка анализа")


    def display_results(self, stats):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        if "general_stats" in stats:
            general_item = self.results_tree.insert('', 'end', text="📊 Общая статистика", open=True)
            for key, value in stats["general_stats"].items():
                if key == "letters_count":
                    key_name = "Количество символов"
                elif key == "words_count":
                    key_name = "Количество слов"
                else:
                    key_name = key
                self.results_tree.insert(general_item, 'end', text=key_name, values=(str(value),))

        if "letters_stats" in stats:
            if "error" in stats["letters_stats"]:
                self.results_tree.insert('', 'end', text="🔤 Статистика букв",
                                        values=(stats["letters_stats"]["error"],))
            else:
                letters_item = self.results_tree.insert('', 'end', text="🔤 Статистика букв", open=True)
                for key, value in stats["letters_stats"].items():
                    if key == "often":
                        self.results_tree.insert(letters_item, 'end',
                                                 text="Самая частая буква",
                                                 values=(f"{value[0]} ({value[1]} раз)",))
                    elif key == "rare":
                        self.results_tree.insert(letters_item, 'end',
                                                 text="Самая редкая буква",
                                                 values=(f"{value[0]} ({value[1]} раз)",))
                    elif key == "median":
                        self.results_tree.insert(letters_item, 'end',
                                                 text="Медианная буква",
                                                 values=(f"{value[0]} ({value[1]} раз)",))
                    elif key == "different_letter":
                        self.results_tree.insert(letters_item, 'end',
                                                 text="Различных букв",
                                                 values=(str(value),))
                    else:
                        self.results_tree.insert(letters_item, 'end', text=key, values=(str(value),))

        if "words_stats" in stats:
            if "error" in stats["words_stats"]:
                self.results_tree.insert('', 'end', text="📝 Статистика слов",
                                        values=(stats["words_stats"]["error"],))
            else:
                words_item = self.results_tree.insert('', 'end', text="📝 Статистика слов", open=True)
                for key, value in stats["words_stats"].items():
                    if key == "min_count":
                        self.results_tree.insert(words_item, 'end',
                                                 text="Минимальное вхождение",
                                                 values=(str(value),))
                    elif key == "max_count":
                        self.results_tree.insert(words_item, 'end',
                                                 text="Максимальное вхождение",
                                                 values=(str(value),))
                    elif key == "words_with_min_count":
                        words_str = ", ".join(value[:5])
                        if len(value) > 5:
                            words_str += "..."
                        self.results_tree.insert(words_item, 'end',
                                                 text="Слова с минимальным кол-вом",
                                                 values=(words_str,))
                    elif key == "words_with_max_count":
                        words_str = ", ".join(value[:5])
                        if len(value) > 5:
                            words_str += "..."
                        self.results_tree.insert(words_item, 'end',
                                                 text="Слова с максимальным кол-вом",
                                                 values=(words_str,))
                    elif key == "unique_count":
                        self.results_tree.insert(words_item, 'end',
                                                 text="Уникальных слов",
                                                 values=(str(value),))
                    else:
                        self.results_tree.insert(words_item, 'end', text=key, values=(str(value),))


    def save_to_json(self):
        if not self.analyzer or not self.analyzer.stats:
            messagebox.showwarning("Предупреждение", "Сначала выполните анализ")
            return
        try:
            filters = self.get_active_filters()
            default_name = "analysis_result.json"
            if self.current_file:
                default_name = f"{Path(self.current_file).stem}_analysis.json"

            file_path = filedialog.asksaveasfilename(
                title="Сохранить результаты",
                defaultextension=".json",
                initialfile=default_name,
                filetypes=[("JSON файлы", "*.json")]
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as fl:
                    json.dump(self.analyzer.stats, fl, ensure_ascii=False, indent=4)
                messagebox.showinfo("Успех", f"Результаты сохранены в:\n{file_path}")
                self.update_status(f"Сохранено в {Path(file_path).name}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении:\n{str(e)}")


    def clear_all(self):
        self.analyzer = None
        self.current_file = None
        self.file_info.delete(1.0, tk.END)
        self.text_display.delete(1.0, tk.END)

        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        self.analyze_btn.config(state='disabled')
        self.save_btn.config(state='disabled')
        self.filter_var.set("all")
        self.update_status("Все данные очищены")


    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update()


    def run(self):
        self.root.mainloop()


# now it should work
if __name__ == "__main__":
    app = TextAnalyzerGUI()
    app.run()