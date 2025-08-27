import gradio as gr
import json
import datetime
import pandas as pd
from typing import Dict, List, Optional
import os

class BudgetManager:
    def __init__(self, data_file: str = "budget_data.json"):
        self.data_file = data_file
        self.data = self.load_data()
        
    def load_data(self) -> Dict:
        """Load budget and expense data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return {
            "monthly_salary": 0,
            "budget_categories": {},
            "expenses": [],
            "savings_goal": 0
        }
    
    def save_data(self):
        """Save current data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def set_monthly_salary(self, salary: float):
        """Set your expected monthly salary"""
        self.data["monthly_salary"] = salary
        self.save_data()
        return f"✅ Monthly salary set to: ${salary:,.2f}"
    
    def set_savings_goal(self, goal: float):
        """Set monthly savings goal"""
        self.data["savings_goal"] = goal
        self.save_data()
        return f"✅ Monthly savings goal set to: ${goal:,.2f}"
    
    def create_budget_category(self, category: str, amount: float, description: str = ""):
        """Create or update a budget category"""
        if not category.strip():
            return "❌ Please enter a category name"
        
        self.data["budget_categories"][category] = {
            "budgeted_amount": amount,
            "description": description
        }
        self.save_data()
        return f"✅ Budget category '{category}' set to: ${amount:,.2f}"
    
    def add_expense(self, category: str, amount: float, description: str = "", date: str = None):
        """Add an expense"""
        if not category.strip():
            return "❌ Please enter a category name"
        
        if date is None or date == "":
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        try:
            # Validate date format
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        expense = {
            "date": date,
            "category": category,
            "amount": amount,
            "description": description
        }
        
        self.data["expenses"].append(expense)
        self.save_data()
        return f"✅ Added expense: ${amount:,.2f} for {category} on {date}"
    
    def get_monthly_expenses(self, year: int = None, month: int = None) -> List[Dict]:
        """Get expenses for a specific month"""
        if year is None or month is None:
            now = datetime.datetime.now()
            year = now.year
            month = now.month
        
        monthly_expenses = []
        for expense in self.data["expenses"]:
            expense_date = datetime.datetime.strptime(expense["date"], "%Y-%m-%d")
            if expense_date.year == year and expense_date.month == month:
                monthly_expenses.append(expense)
        
        return monthly_expenses
    
    def calculate_category_spending(self, year: int = None, month: int = None) -> Dict[str, float]:
        """Calculate total spending by category for a given month"""
        monthly_expenses = self.get_monthly_expenses(year, month)
        category_totals = {}
        
        for expense in monthly_expenses:
            category = expense["category"]
            amount = expense["amount"]
            category_totals[category] = category_totals.get(category, 0) + amount
        
        return category_totals
    
    def get_budget_overview(self):
        """Get comprehensive budget overview"""
        salary = self.data["monthly_salary"]
        savings_goal = self.data["savings_goal"]
        
        overview = f"""
# 💰 Budget Overview

**Monthly Salary:** ${salary:,.2f}
**Savings Goal:** ${savings_goal:,.2f}
"""
        
        if not self.data["budget_categories"]:
            overview += "\n⚠️ No budget categories set yet. Create some categories below!"
            return overview
        
        total_budgeted = sum(cat["budgeted_amount"] for cat in self.data["budget_categories"].values())
        total_budgeted += savings_goal
        
        overview += f"**Total Budgeted (including savings):** ${total_budgeted:,.2f}\n"
        
        remaining = salary - total_budgeted
        overview += f"**Remaining after budget:** ${remaining:,.2f}\n\n"
        
        if remaining < 0:
            overview += "⚠️ **WARNING: You're over budget!**\n\n"
        elif remaining > 0:
            overview += "✅ **You have room in your budget**\n\n"
        
        overview += "## Budget Categories:\n\n"
        
        for category, details in self.data["budget_categories"].items():
            amount = details["budgeted_amount"]
            desc = details["description"]
            percentage = (amount / salary * 100) if salary > 0 else 0
            overview += f"- **{category}:** ${amount:,.2f} ({percentage:.1f}%) - {desc}\n"
        
        return overview
    
    def get_spending_analysis(self):
        """Get detailed spending analysis for current month"""
        now = datetime.datetime.now()
        year, month = now.year, now.month
        
        analysis = f"# 📊 Spending Analysis - {datetime.date(year, month, 1).strftime('%B %Y')}\n\n"
        
        category_spending = self.calculate_category_spending(year, month)
        total_spent = sum(category_spending.values())
        
        analysis += f"**Total Spent:** ${total_spent:,.2f}\n"
        
        if self.data["monthly_salary"] > 0:
            remaining_salary = self.data["monthly_salary"] - total_spent
            analysis += f"**Remaining from Salary:** ${remaining_salary:,.2f}\n\n"
        
        if not category_spending:
            analysis += "No expenses recorded for this month yet.\n"
            return analysis
        
        analysis += "## Spending by Category:\n\n"
        
        for category, spent in category_spending.items():
            budgeted = self.data["budget_categories"].get(category, {}).get("budgeted_amount", 0)
            
            if budgeted > 0:
                percentage_used = (spent / budgeted) * 100
                remaining = budgeted - spent
                status = "✅" if spent <= budgeted else "⚠️"
                analysis += f"- **{category}:** ${spent:,.2f} / ${budgeted:,.2f} ({percentage_used:.1f}%) {status}\n"
                if remaining < 0:
                    analysis += f"  - Over budget by ${abs(remaining):,.2f}\n"
            else:
                analysis += f"- **{category}:** ${spent:,.2f} (No budget set)\n"
        
        # Check savings progress
        if self.data["savings_goal"] > 0:
            potential_savings = self.data["monthly_salary"] - total_spent
            savings_progress = (potential_savings / self.data["savings_goal"]) * 100
            analysis += f"\n## 💰 Savings Progress:\n"
            analysis += f"- **Potential Savings:** ${potential_savings:,.2f}\n"
            analysis += f"- **Savings Goal:** ${self.data['savings_goal']:,.2f}\n"
            analysis += f"- **Progress:** {savings_progress:.1f}%\n"
        
        return analysis
    
    def get_recent_expenses_df(self, limit: int = 20):
        """Get recent expenses as DataFrame for display"""
        if not self.data["expenses"]:
            return pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])
        
        recent_expenses = sorted(self.data["expenses"], key=lambda x: x["date"], reverse=True)[:limit]
        
        df_data = []
        for expense in recent_expenses:
            df_data.append({
                "Date": expense["date"],
                "Category": expense["category"],
                "Amount": f"${expense['amount']:,.2f}",
                "Description": expense["description"]
            })
        
        return pd.DataFrame(df_data)
    
    def get_budget_recommendations(self):
        """Get budget recommendations based on 50/30/20 rule"""
        salary = self.data["monthly_salary"]
        if salary <= 0:
            return "Please set your monthly salary first to get recommendations."
        
        recommendations = f"""
# 💡 Budget Recommendations (50/30/20 Rule)

Based on your monthly salary of ${salary:,.2f}:

- **Needs (Housing, Food, Utilities):** ${salary * 0.50:,.2f} (50%)
- **Wants (Entertainment, Dining Out):** ${salary * 0.30:,.2f} (30%)
- **Savings & Debt Repayment:** ${salary * 0.20:,.2f} (20%)

## Suggested Monthly Categories:

- **Housing:** ${salary * 0.30:,.2f} (30% of income)
- **Food:** ${salary * 0.15:,.2f} (15% of income)
- **Utilities:** ${salary * 0.05:,.2f} (5% of income)
- **Transportation:** ${salary * 0.12:,.2f} (12% of income)
- **Entertainment:** ${salary * 0.18:,.2f} (18% of income)
- **Savings:** ${salary * 0.20:,.2f} (20% of income)

*Note: Adjust these percentages based on your personal situation and priorities.*
"""
        return recommendations
    
    def delete_last_expense(self):
        """Delete the most recent expense"""
        if not self.data["expenses"]:
            return "❌ No expenses to delete"
        
        removed = self.data["expenses"].pop()
        self.save_data()
        return f"✅ Deleted expense: ${removed['amount']:,.2f} for {removed['category']} on {removed['date']}"

# Initialize the budget manager
budget_manager = BudgetManager()

# Define Gradio interface functions
def update_salary(salary):
    try:
        return budget_manager.set_monthly_salary(float(salary))
    except ValueError:
        return "❌ Please enter a valid number"

def update_savings_goal(goal):
    try:
        return budget_manager.set_savings_goal(float(goal))
    except ValueError:
        return "❌ Please enter a valid number"

def add_budget_category(category, amount, description):
    try:
        return budget_manager.create_budget_category(category, float(amount), description)
    except ValueError:
        return "❌ Please enter a valid amount"

def add_new_expense(category, amount, description, date):
    try:
        return budget_manager.add_expense(category, float(amount), description, date)
    except ValueError:
        return "❌ Please enter a valid amount"

def refresh_overview():
    return budget_manager.get_budget_overview()

def refresh_analysis():
    return budget_manager.get_spending_analysis()

def refresh_expenses():
    return budget_manager.get_recent_expenses_df()

def get_recommendations():
    return budget_manager.get_budget_recommendations()

def delete_expense():
    return budget_manager.delete_last_expense()

# Create Gradio interface
with gr.Blocks(title="💰 Personal Budget Manager", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 💰 Personal Budget & Expense Manager")
    gr.Markdown("Manage your budget and track expenses with this interactive tool!")
    
    with gr.Tabs():
        # Setup Tab
        with gr.Tab("⚙️ Setup"):
            gr.Markdown("## Initial Setup")
            
            with gr.Row():
                with gr.Column():
                    salary_input = gr.Number(label="Monthly Salary ($)", value=0, precision=2)
                    salary_btn = gr.Button("Set Salary", variant="primary")
                    salary_status = gr.Textbox(label="Status", interactive=False)
                
                with gr.Column():
                    savings_input = gr.Number(label="Monthly Savings Goal ($)", value=0, precision=2)
                    savings_btn = gr.Button("Set Savings Goal", variant="primary")
                    savings_status = gr.Textbox(label="Status", interactive=False)
            
            gr.Markdown("## Create Budget Categories")
            with gr.Row():
                category_name = gr.Textbox(label="Category Name", placeholder="e.g., Housing, Food, Entertainment")
                category_amount = gr.Number(label="Budgeted Amount ($)", value=0, precision=2)
                category_desc = gr.Textbox(label="Description (optional)", placeholder="Brief description")
            
            category_btn = gr.Button("Add/Update Category", variant="primary")
            category_status = gr.Textbox(label="Status", interactive=False)
        
        # Expenses Tab
        with gr.Tab("💸 Add Expenses"):
            gr.Markdown("## Add New Expense")
            
            with gr.Row():
                expense_category = gr.Textbox(label="Category", placeholder="e.g., Food, Transportation")
                expense_amount = gr.Number(label="Amount ($)", value=0, precision=2)
            
            with gr.Row():
                expense_desc = gr.Textbox(label="Description (optional)", placeholder="Brief description of the expense")
                expense_date = gr.Textbox(label="Date (YYYY-MM-DD)", placeholder="Leave empty for today", value="")
            
            expense_btn = gr.Button("Add Expense", variant="primary")
            expense_status = gr.Textbox(label="Status", interactive=False)
            
            gr.Markdown("## Recent Expenses")
            expenses_df = gr.Dataframe(
                headers=["Date", "Category", "Amount", "Description"],
                datatype=["str", "str", "str", "str"],
                interactive=False,
                value=budget_manager.get_recent_expenses_df()
            )
            
            with gr.Row():
                refresh_expenses_btn = gr.Button("Refresh Expenses", variant="secondary")
                delete_expense_btn = gr.Button("Delete Last Expense", variant="secondary")
            
            delete_status = gr.Textbox(label="Delete Status", interactive=False)
        
        # Overview Tab
        with gr.Tab("📊 Budget Overview"):
            overview_display = gr.Markdown(value=budget_manager.get_budget_overview())
            refresh_overview_btn = gr.Button("Refresh Overview", variant="primary")
        
        # Analysis Tab
        with gr.Tab("📈 Spending Analysis"):
            analysis_display = gr.Markdown(value=budget_manager.get_spending_analysis())
            refresh_analysis_btn = gr.Button("Refresh Analysis", variant="primary")
        
        # Recommendations Tab
        with gr.Tab("💡 Recommendations"):
            recommendations_display = gr.Markdown(value=budget_manager.get_budget_recommendations())
            refresh_recommendations_btn = gr.Button("Refresh Recommendations", variant="primary")
    
    # Event handlers
    salary_btn.click(update_salary, inputs=[salary_input], outputs=[salary_status])
    savings_btn.click(update_savings_goal, inputs=[savings_input], outputs=[savings_status])
    category_btn.click(add_budget_category, inputs=[category_name, category_amount, category_desc], outputs=[category_status])
    expense_btn.click(add_new_expense, inputs=[expense_category, expense_amount, expense_desc, expense_date], outputs=[expense_status])
    
    refresh_overview_btn.click(refresh_overview, outputs=[overview_display])
    refresh_analysis_btn.click(refresh_analysis, outputs=[analysis_display])
    refresh_expenses_btn.click(refresh_expenses, outputs=[expenses_df])
    refresh_recommendations_btn.click(get_recommendations, outputs=[recommendations_display])
    delete_expense_btn.click(delete_expense, outputs=[delete_status])

# Launch the app
if __name__ == "__main__":
    app.launch(share=True)