import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime


DATA_FILE = "expenses.json"
DATE_FORMAT = "гггг-мм-дд"
CATEGORIES = ('Еда', 'Транспорт', 'Развлечения', 'Здоровье', 'Дом', 'Другое')
FILTER_CATEGORIES = ('Все',) + CATEGORIES


expenses = []
filtered_expenses = []


tree = None
status_var = None
amount_entry = None
category_combo = None
date_entry = None
filter_category = None
date_from_entry = None
date_to_entry = None


def load_data():
    global expenses
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                expenses = json.load(f)
        except (json.JSONDecodeError, IOError):
            expenses = []
    else:
        expenses = []


def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(expenses, f, ensure_ascii=False, indent=4)



def validate_date(date_str):

    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return True
    except ValueError:
        return False


def parse_date(date_str):

    return datetime.strptime(date_str, DATE_FORMAT)


def is_match(expense, category, date_from, date_to):


    if category != 'Все' and expense['category'] != category:
        return False

    exp_date = parse_date(expense['date'])

    # Фильтр по дате "от"
    if date_from and exp_date < parse_date(date_from):
        return False

    # Фильтр по дате "до"
    if date_to and exp_date > parse_date(date_to):
        return False

    return True



def update_display():


    for row in tree.get_children():
        tree.delete(row)


    total = 0.0
    for idx, exp in enumerate(filtered_expenses, start=1):
        tree.insert('', tk.END, values=(idx, exp['amount'], exp['category'], exp['date']))
        total += exp['amount']

    status_var.set(f"Показано: {len(filtered_expenses)} | Сумма: {total:.2f}")



def add_expense():
    global expenses


    try:
        amount = float(amount_entry.get())
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Ошибка", "Сумма должна быть положительным числом.")
        return


    category = category_combo.get().strip()
    if not category:
        messagebox.showerror("Ошибка", "Введите или выберите категорию.")
        return


    date_str = date_entry.get().strip()
    if not validate_date(date_str):
        messagebox.showerror("Ошибка", f"Дата должна быть в формате {DATE_FORMAT} (пример: 2025-04-25).")
        return


    new_id = max((e['id'] for e in expenses), default=0) + 1
    new_expense = {
        'id': new_id,
        'amount': amount,
        'category': category,
        'date': date_str
    }
    expenses.append(new_expense)
    save_data()
    apply_filter()


    amount_entry.delete(0, tk.END)
    category_combo.set('')
    date_entry.delete(0, tk.END)
    date_entry.insert(0, datetime.today().strftime(DATE_FORMAT))

    status_var.set(f"Добавлен расход: {amount} ({category})")



def apply_filter():
    global filtered_expenses

    cat = filter_category.get()
    date_from_str = date_from_entry.get().strip()
    date_to_str = date_to_entry.get().strip()


    for date_str, field_name in [(date_from_str, "от"), (date_to_str, "до")]:
        if date_str and not validate_date(date_str):
            messagebox.showerror("Ошибка", f"Неверный формат даты '{field_name}'. Используйте {DATE_FORMAT}.")
            return


    filtered_expenses = [
        e for e in expenses
        if is_match(e, cat, date_from_str, date_to_str)
    ]
    update_display()


def clear_filter():
    filter_category.set('Все')
    date_from_entry.delete(0, tk.END)
    date_to_entry.delete(0, tk.END)
    apply_filter()



def delete_selected():
    global expenses
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Внимание", "Не выбрана запись для удаления.")
        return

    item_values = tree.item(selected[0])['values']
    idx_in_filtered = int(item_values[0]) - 1

    if 0 <= idx_in_filtered < len(filtered_expenses):
        expense_id = filtered_expenses[idx_in_filtered]['id']
        confirm = messagebox.askyesno("Подтверждение", f"Удалить расход с ID {expense_id}?")
        if confirm:
            expenses = [e for e in expenses if e['id'] != expense_id]
            save_data()
            apply_filter()
            status_var.set(f"Запись ID {expense_id} удалена.")



def calc_sum_period():
    date_from_str = date_from_entry.get().strip()
    date_to_str = date_to_entry.get().strip()

    if not date_from_str or not date_to_str:
        messagebox.showwarning("Внимание", "Укажите обе даты (от и до) для подсчёта суммы.")
        return

    if not (validate_date(date_from_str) and validate_date(date_to_str)):
        messagebox.showerror("Ошибка", f"Неверный формат даты. Используйте {DATE_FORMAT}.")
        return

    date_from = parse_date(date_from_str)
    date_to = parse_date(date_to_str)

    total = sum(e['amount'] for e in expenses
                if date_from <= parse_date(e['date']) <= date_to)

    messagebox.showinfo("Сумма за период",
                        f"Общая сумма расходов с {date_from_str} по {date_to_str}: {total:.2f}")



def build_input_section(parent):
    global amount_entry, category_combo, date_entry

    frame = ttk.LabelFrame(parent, text="Добавить расход", padding=10)
    frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    amount_entry = ttk.Entry(frame, width=15)
    amount_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    category_combo = ttk.Combobox(frame, width=15, values=CATEGORIES)
    category_combo.grid(row=0, column=3, padx=5, pady=5)

    ttk.Label(frame, text=f"Дата ({DATE_FORMAT}):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
    date_entry = ttk.Entry(frame, width=12)
    date_entry.grid(row=0, column=5, padx=5, pady=5)
    date_entry.insert(0, datetime.today().strftime(DATE_FORMAT))

    add_btn = ttk.Button(frame, text="Добавить расход", command=add_expense)
    add_btn.grid(row=0, column=6, padx=10, pady=5)


def build_filter_section(parent):
    global filter_category, date_from_entry, date_to_entry

    frame = ttk.LabelFrame(parent, text="Фильтры", padding=10)
    frame.pack(fill="x", padx=10, pady=5)

    ttk.Label(frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    filter_category = ttk.Combobox(frame, width=15, values=FILTER_CATEGORIES)
    filter_category.set('Все')
    filter_category.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame, text="Дата от:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    date_from_entry = ttk.Entry(frame, width=12)
    date_from_entry.grid(row=0, column=3, padx=5, pady=5)

    ttk.Label(frame, text="Дата до:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
    date_to_entry = ttk.Entry(frame, width=12)
    date_to_entry.grid(row=0, column=5, padx=5, pady=5)

    filter_btn = ttk.Button(frame, text="Применить фильтр", command=apply_filter)
    filter_btn.grid(row=0, column=6, padx=5, pady=5)

    clear_btn = ttk.Button(frame, text="Сбросить фильтр", command=clear_filter)
    clear_btn.grid(row=0, column=7, padx=5, pady=5)

    sum_btn = ttk.Button(frame, text="Подсчитать сумму за период (из фильтра)", command=calc_sum_period)
    sum_btn.grid(row=1, column=0, columnspan=8, pady=5)


def build_table_section(parent):
    global tree

    frame = ttk.LabelFrame(parent, text="Список расходов", padding=10)
    frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ('num', 'amount', 'category', 'date')
    tree = ttk.Treeview(frame, columns=columns, show='headings')
    tree.heading('num', text='№')
    tree.heading('amount', text='Сумма')
    tree.heading('category', text='Категория')
    tree.heading('date', text='Дата')
    tree.column('num', width=50, anchor='center')
    tree.column('amount', width=120, anchor='e')
    tree.column('category', width=150)
    tree.column('date', width=120, anchor='center')
    tree.pack(side='left', fill='both', expand=True)

    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    scrollbar.pack(side='right', fill='y')
    tree.configure(yscrollcommand=scrollbar.set)


def build_gui():
    global status_var

    root = tk.Tk()
    root.title("Expense Tracker")
    root.geometry("900x600")
    root.resizable(True, True)

    build_input_section(root)
    build_filter_section(root)
    build_table_section(root)

    del_btn = ttk.Button(root, text="Удалить выбранную запись", command=delete_selected)
    del_btn.pack(pady=5)

    status_var = tk.StringVar()
    status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    return root



def main():
    global filtered_expenses
    load_data()
    filtered_expenses = expenses[:]
    root = build_gui()
    update_display()
    root.mainloop()


if __name__ == "__main__":
    main()