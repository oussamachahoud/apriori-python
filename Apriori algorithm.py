import pandas as pd
from itertools import combinations
from tkinter import Tk, Label, Button, Entry, Frame, Text, ttk ,messagebox ,filedialog, Toplevel, Scrollbar, Canvas
import os

# Step 1: Data Preparation (similar to your code)
data = pd.read_csv('heart_failure_clinical_records_dataset.csv')

data['creatinine_phosphokinase'] = data['creatinine_phosphokinase'].apply(lambda x: 1 if x > 200 else 0)
data['ejection_fraction'] = data['ejection_fraction'].apply(lambda x: 1 if x > 50 and x < 70 else 0)
data['platelets'] = data['platelets'].apply(lambda x: 1 if x > 150000 and x < 450000 else 0)
data['serum_creatinine'] = data['serum_creatinine'].apply(lambda x: 1 if x > 0.6 and x < 1.1 else 0)
data['serum_sodium'] = data['serum_sodium'].apply(lambda x: 1 if x > 135 and x < 145 else 0)
data['old'] = data['age'].apply(lambda x: 1 if x > 60  else 0)
data = data.drop(columns=['age', 'time',  'sex'])

transactions = data.apply(lambda row: [col for col in data.columns if row[col] == 1], axis=1).tolist()


# Helper functions
def calculate_support(itemset, transactions):
    count = sum(1 for transaction in transactions if set(itemset).issubset(set(transaction)))
    return count / len(transactions)


def generate_candidates(previous_itemsets, k):
    candidates = []
    n = len(previous_itemsets)
    for i in range(n):
        for j in range(i + 1, n):
            candidate = sorted(list(set(previous_itemsets[i]) | set(previous_itemsets[j])))
            if len(candidate) == k and candidate not in candidates:
                candidates.append(candidate)
    return candidates


def filter_itemsets_by_support(candidates, transactions, min_support):
    frequent_itemsets = []
    for itemset in candidates:
        support = calculate_support(itemset, transactions)
        if support >= min_support:
            frequent_itemsets.append((itemset, support))
    return frequent_itemsets


def apriori(transactions, min_support):
    k = 1
    frequent_itemsets = []
    items = sorted({item for transaction in transactions for item in transaction})
    candidates = [[item] for item in items]

    tables = []  # To store C and L tables for display later
    while candidates:
        filtered_itemsets = filter_itemsets_by_support(candidates, transactions, min_support)
        tables.append((f"C{k}", [(itemset, calculate_support(itemset, transactions)) for itemset in candidates]))
        tables.append((f"L{k}", filtered_itemsets))
        frequent_itemsets.extend(filtered_itemsets)
        candidates = generate_candidates([itemset for itemset, _ in filtered_itemsets], k + 1)
        k += 1

    return frequent_itemsets, tables


def generate_association_rules(frequent_itemsets, transactions, min_confidence):
    rules = []
    for itemset, support in frequent_itemsets:
        if len(itemset) > 1:
            for i in range(1, len(itemset)):
                antecedents = generate_combinations(itemset, i)
                for antecedent in antecedents:
                    consequent = list(set(itemset) - set(antecedent))
                    if consequent:
                        antecedent_support = calculate_support(antecedent, transactions)
                        if antecedent_support > 0:
                            confidence = support / antecedent_support
                            if confidence >= min_confidence:
                                rules.append({
                                    'antecedent': antecedent,
                                    'consequent': consequent,
                                    'support': support,
                                    'confidence': confidence
                                })
    return rules


def generate_combinations(itemset, length):
    return [list(comb) for comb in combinations(itemset, length)]


# GUI Functions
def display_results(tables, rules, min_support):
    # Clear existing tabs
    for tab in notebook.tabs():
        notebook.forget(tab)

    # Display C and L tables
    for title, data in tables:
        frame = Frame(notebook)
        notebook.add(frame, text=title)
        tree = ttk.Treeview(frame, columns=("Itemset", "Support"), show='headings')
        tree.heading("Itemset", text="Itemset")
        tree.heading("Support", text="Support")
        tree.pack(fill='both', expand=True)

        for itemset, support in data:
            tag = ""
            if support < min_support and "C" in title:  # Highlight rows in C tables below min_support
                tag = "below_support"
            tree.insert("", "end", values=(itemset, f"{support:.2f}"), tags=(tag,))

        # Configure row coloring
        tree.tag_configure("below_support", background="red")  # Rows below support threshold will appear red

    # Display Association Rules
    frame = Frame(notebook)
    notebook.add(frame, text="Association Rules")
    tree = ttk.Treeview(frame, columns=("Rules","Support","confidence" ), show='headings')
    tree.heading("Rules", text="Rules")
    tree.heading("Support", text="Support")
    tree.heading("confidence", text="confidence")
    #text = Text(frame, wrap='word', font=('Arial', 12))
    tree.pack(fill='both', expand=True)
    
    
    with open("output.txt", "a") as file:
       for rule in rules:
           antecedent = ', '.join(rule['antecedent'])
           consequent = ', '.join(rule['consequent'])
           file.write(f"{antecedent} => {consequent} \n")
           tree.insert("",'end',values=( f"{antecedent} => {consequent}" , f"Support: {rule['support']:.2f}", f"Confidence: {rule['confidence']:.2f}"))


def run_apriori():
    file_path = "output.txt"
    if os.path.exists(file_path):
      os.remove(file_path)
    if not support_entry.get() or not confidence_entry.get():
         messagebox.showerror("Error", "Entry is empty. Please provide a value.")
    elif  float(support_entry.get()) > 100 or  float(confidence_entry.get()) > 100:     
         messagebox.showerror("Error", "Entry is higher than 100. Please provide a value.")
    else:
        min_support = float(support_entry.get())/100
        min_confidence = float(confidence_entry.get())/100
    
    
        frequent_itemsets, tables = apriori(transactions, min_support)
        rules = generate_association_rules(frequent_itemsets, transactions, min_confidence)
        display_results(tables, rules, min_support)


def display_csv():
    
    
    try:
        
        

        # إنشاء نافذة جديدة
        new_window = Toplevel(main_window)
        new_window.title("CSV Nettoyage")
        new_window.geometry("920x500")

        
 
 
        # إنشاء إطار للتمرير الأفقي والعمودي
        canvas = Canvas(new_window)
        scrollbar_x = Scrollbar(new_window, orient="horizontal", command=canvas.xview)
        scrollbar_y = Scrollbar(new_window, orient="vertical", command=canvas.yview)
        frame = Frame(canvas)

        # ربط التمرير بـ Canvas
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)

        scrollbar_x.pack(side="bottom", fill="x")
        scrollbar_y.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
       # عرض البيانات في Treeview داخل النافذة الجديدة
        tree = ttk.Treeview(frame, columns=list(data.columns), show="headings", height=25)
        tree.pack(side="top", fill="both", expand=True)
        
        # إعداد الأعمدة
        tree["columns"] = list(data.columns)
        tree["show"] = "headings"

        for col in data.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # إدراج الصفوف
        for _, row in data.iterrows():
            tree.insert("", "end", values=list(row))
        
        
        frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    except Exception as e:
        # إذا حدث خطأ أثناء قراءة الملف، عرض رسالة خطأ
        error_window = Toplevel(main_window)
        error_window.title("Error")
        error_label = Label(error_window, text=f"Error: {e}", fg="red")
        error_label.pack(padx=10, pady=10)
        
        
        
# Main GUI
main_window = Tk()
main_window.title("Apriori Algorithm")
main_window.geometry("1200x800")  # Larger window for all content

# Input Section
input_frame = Frame(main_window)
input_frame.pack(fill='x', padx=10, pady=10)

Label(input_frame, text="Minimum Support %:").grid(row=0, column=0, padx=10, pady=10)
support_entry = Entry(input_frame)
support_entry.grid(row=0, column=1, padx=10, pady=10)
support_entry.insert(0, "30")

Label(input_frame, text="Minimum Confidence %:").grid(row=0, column=2, padx=10, pady=10)
confidence_entry = Entry(input_frame)
confidence_entry.grid(row=0, column=3, padx=10, pady=10)
confidence_entry.insert(0, "50")

Button(input_frame, text="Run Apriori", command=run_apriori).grid(row=0, column=4, padx=10, pady=10)
Button(input_frame, text="display nettoyage", command=display_csv).grid(row=0, column=5, padx=10, pady=10)

# Notebook for tables and results
notebook = ttk.Notebook(main_window)
notebook.pack(fill='both', expand=True, padx=10, pady=10)

main_window.mainloop()