import tkinter as tk
from tkinter import messagebox
import random

class PoleChudes:
    def __init__(self, root):
        self.root = root
        self.root.title("ПОЛЕ ЧУДЕС")
        self.root.geometry("600x650")
        self.root.resizable(False, False)
        
        # Цветовая схема
        self.colors = {
            "bg": "white",
            "button": "#4a90e2",
            "button_text": "white",
            "correct": "green",
            "incorrect": "red",
            "letter": "#FFD700",
            "display": "#f8f8f8",
            "undo": "#ff9800",  # оранжевый для кнопки отмены
        }
        
        self.word_to_guess = ""
        self.scrambled_letters = []
        self.user_sequence = []
        
        self.create_widgets()
        self.reset_to_initial_state()
        
    def create_widgets(self):
        # Заголовок
        self.title_label = tk.Label(self.root, text="ПОЛЕ ЧУДЕС", 
                                    font=("Arial", 20, "bold"))
        self.title_label.pack(pady=10)
        
        # === Фрейм для ввода слова ===
        self.input_frame = tk.Frame(self.root)
        
        # Заголовок поля ввода
        self.input_label = tk.Label(self.input_frame, text="Введите слово:", 
                                   font=("Arial", 11))
        self.input_label.pack(side=tk.LEFT, padx=5)
        
        # Поле ввода
        self.word_entry = tk.Entry(self.input_frame, width=20, 
                                  font=("Arial", 12), relief="solid", bd=1)
        self.word_entry.pack(side=tk.LEFT, padx=5)
        
        # Кнопка "Начать"
        self.start_button = tk.Button(self.input_frame, text="Начать", 
                                      command=self.start_game, 
                                      font=("Arial", 11),
                                      bg=self.colors["button"], fg="white",
                                      padx=15, pady=3)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Перепутанные буквы
        self.scrambled_label = tk.Label(self.root, text="Перепутанные буквы:", 
                                       font=("Arial", 11))
        self.scrambled_label.pack(pady=(10, 5))
        
        self.scrambled_display = tk.Label(self.root, text="", 
                                         font=("Arial", 16, "bold"),
                                         bg=self.colors["display"],
                                         width=30, height=2, 
                                         relief="solid", bd=1)
        self.scrambled_display.pack(pady=5)
        
        # Разделитель
        self.separator = tk.Frame(self.root, height=2, bg="lightgray")
        self.separator.pack(fill="x", padx=20, pady=15)
        
        # Инструкция
        self.instruction_label = tk.Label(self.root, text="Соберите слово:", 
                                         font=("Arial", 11))
        self.instruction_label.pack(pady=5)
        
        self.word_display = tk.Label(self.root, text="", 
                                    font=("Courier", 18, "bold"),
                                    bg=self.colors["display"],
                                    width=25, height=2, 
                                    relief="solid", bd=1)
        self.word_display.pack(pady=10)
        
        # Фрейм для кнопок с буквами
        self.letters_frame = tk.Frame(self.root)
        
        self.letter_buttons = []
        
        # Фрейм для управления игрой (отмена, проверка)
        game_control_frame = tk.Frame(self.root)
        game_control_frame.pack(pady=10)
        
        # Кнопка "Назад" (отмена последнего действия)
        self.undo_button = tk.Button(game_control_frame, text="← Назад", 
                                     command=self.undo_last_letter,
                                     font=("Arial", 11),
                                     bg=self.colors["undo"], fg="white",
                                     padx=20, pady=6,
                                     state=tk.DISABLED)
        self.undo_button.pack(side=tk.LEFT, padx=10)
        
        # Кнопка "Проверить" (переименована в "Поделиться")
        self.check_button = tk.Button(game_control_frame, text="Поделиться", 
                                      command=self.check_word, 
                                      font=("Arial", 11),
                                      bg=self.colors["button"], fg="white",
                                      padx=20, pady=6,
                                      state=tk.DISABLED)
        self.check_button.pack(side=tk.LEFT, padx=10)
        
        # Фрейм для кнопок управления игрой
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=20)
        
        # Кнопка "Новая игра"
        self.new_game_button = tk.Button(control_frame, text="Новая игра", 
                                         command=self.new_game, 
                                         font=("Arial", 11),
                                         bg=self.colors["button"], fg="white",
                                         padx=25, pady=6)
        self.new_game_button.pack()
        
        # Результат
        self.result_label = tk.Label(self.root, text="", 
                                    font=("Arial", 12),
                                    height=2)
        self.result_label.pack(pady=15)
    
    def reset_to_initial_state(self):
        """Устанавливает начальное состояние как на фото"""
        # Показываем поле ввода
        self.input_frame.pack(pady=5)
        
        # Очищаем и показываем тире для перепутанных букв
        self.scrambled_display.config(text="- - - -")
        
        # Очищаем и показываем тире для собираемого слова
        self.word_display.config(text="- - - -")
        
        # Скрываем кнопки с буквами
        self.letters_frame.pack_forget()
        
        # Очищаем кнопки букв
        for button in self.letter_buttons:
            button.destroy()
        self.letter_buttons.clear()
        
        # Деактивируем кнопки управления игрой
        self.check_button.config(state=tk.DISABLED, bg="gray")
        self.undo_button.config(state=tk.DISABLED, bg="gray")
        
        # Очищаем результат
        self.result_label.config(text="")
        
        # Очищаем поле ввода
        self.word_entry.delete(0, tk.END)
        
        # Ставим фокус на поле ввода
        self.word_entry.focus_set()
    
    def scramble_letters(self, word):
        """Перемешивает буквы в слове"""
        letters = list(word.upper())
        while True:
            random.shuffle(letters)
            if ''.join(letters) != word.upper():
                break
        return letters
    
    def create_letter_buttons(self):
        """Создает кнопки для каждой перепутанной буквы"""
        # Очищаем предыдущие кнопки
        for button in self.letter_buttons:
            button.destroy()
        self.letter_buttons.clear()
        
        # Создаем новые кнопки
        for i, letter in enumerate(self.scrambled_letters):
            button = tk.Button(self.letters_frame, text=letter, 
                              font=("Arial", 14, "bold"),
                              width=4, height=2,
                              bg=self.colors["letter"],
                              command=lambda l=letter: self.add_letter(l))
            button.grid(row=0, column=i, padx=4, pady=5)
            self.letter_buttons.append(button)
    
    def update_word_display(self):
        """Обновляет отображение собираемого слова"""
        display_text = ""
        for i in range(len(self.word_to_guess)):
            if i < len(self.user_sequence):
                display_text += self.user_sequence[i]
            else:
                display_text += "?"
            if i < len(self.word_to_guess) - 1:
                display_text += " "
        
        self.word_display.config(text=display_text)
    
    def update_undo_button_state(self):
        """Обновляет состояние кнопки 'Назад'"""
        if self.user_sequence:
            self.undo_button.config(state=tk.NORMAL, bg=self.colors["undo"])
        else:
            self.undo_button.config(state=tk.DISABLED, bg="gray")
    
    def start_game(self):
        """Начинает новую игру с введенным словом"""
        word = self.word_entry.get().strip()
        
        if not word:
            messagebox.showwarning("Внимание", "Введите слово для игры!")
            return
        
        if not word.isalpha():
            messagebox.showwarning("Внимание", "Слово должно содержать только буквы!")
            return
        
        if len(word) < 3:
            messagebox.showwarning("Внимание", "Слово должно содержать минимум 3 буквы!")
            return
        
        self.word_to_guess = word.upper()
        self.scrambled_letters = self.scramble_letters(word)
        self.user_sequence = []
        
        # Скрываем поле ввода
        self.input_frame.pack_forget()
        
        # Показываем кнопки с буквами
        self.letters_frame.pack(pady=15)
        
        # Обновляем отображение
        self.scrambled_display.config(text=" ".join(self.scrambled_letters))
        
        # Отображаем вопросительные знаки
        self.update_word_display()
        self.result_label.config(text="")
        
        # Создаем кнопки с буквами
        self.create_letter_buttons()
        
        # Активируем кнопки управления
        self.check_button.config(state=tk.NORMAL, bg=self.colors["button"])
        self.update_undo_button_state()
        
        # Фокус на кнопки букв
        if self.letter_buttons:
            self.letter_buttons[0].focus_set()
    
    def add_letter(self, letter):
        """Добавляет букву к собираемому слову"""
        if len(self.user_sequence) < len(self.word_to_guess):
            self.user_sequence.append(letter)
            
            # Обновляем отображение
            self.update_word_display()
            
            # Делаем кнопку неактивной после нажатия
            for button in self.letter_buttons:
                if button["text"] == letter and button["state"] != tk.DISABLED:
                    button.config(state=tk.DISABLED, bg="lightgray")
                    break
            
            # Обновляем состояние кнопки "Назад"
            self.update_undo_button_state()
    
    def undo_last_letter(self):
        """Отменяет последнюю добавленную букву"""
        if self.user_sequence:
            # Удаляем последнюю букву из последовательности
            removed_letter = self.user_sequence.pop()
            
            # Обновляем отображение слова
            self.update_word_display()
            
            # Активируем соответствующую кнопку буквы
            for button in self.letter_buttons:
                if button["text"] == removed_letter:
                    button.config(state=tk.NORMAL, bg=self.colors["letter"])
                    break
            
            # Обновляем состояние кнопки "Назад"
            self.update_undo_button_state()
            
            # Если все буквы удалены, деактивируем кнопку "Поделиться"
            if not self.user_sequence:
                self.check_button.config(state=tk.NORMAL, bg=self.colors["button"])
    
    def check_word(self):
        """Проверяет, правильно ли собрано слово (Поделиться)"""
        user_word = ''.join(self.user_sequence)
        
        if len(user_word) != len(self.word_to_guess):
            messagebox.showwarning("Внимание", 
                                 f"Нужно собрать слово из {len(self.word_to_guess)} букв!")
            return
        
        if user_word == self.word_to_guess:
            self.result_label.config(text="✓ Правильно! Слово собрано верно.", 
                                   fg=self.colors["correct"])
            
            # Подсвечиваем результат
            self.word_display.config(bg="#e8f5e8")
            
            # Деактивируем все кнопки
            for button in self.letter_buttons:
                button.config(state=tk.DISABLED)
            
            self.check_button.config(state=tk.DISABLED, bg="gray")
            self.undo_button.config(state=tk.DISABLED, bg="gray")
        else:
            self.result_label.config(text=f"✗ Неверно. Правильное слово: {self.word_to_guess}", 
                                   fg=self.colors["incorrect"])
            
            # Подсвечиваем результат
            self.word_display.config(bg="#fce8e8")
            
            # Показываем правильное слово
            correct_display = " ".join(list(self.word_to_guess))
            self.word_display.config(text=correct_display)
            
            # Деактивируем все кнопки
            for button in self.letter_buttons:
                button.config(state=tk.DISABLED)
            
            self.check_button.config(state=tk.DISABLED, bg="gray")
            self.undo_button.config(state=tk.DISABLED, bg="gray")
    
    def new_game(self):
        """Начинает новую игру - возвращает форму в исходное состояние как на фото"""
        self.reset_to_initial_state()

def main():
    root = tk.Tk()
    app = PoleChudes(root)
    root.mainloop()

if __name__ == "__main__":
    main()