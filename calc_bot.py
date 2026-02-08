import ast
import operator as op
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8434914963:AAGRJgsezzBKZBxsWgB9baNwymLr0iqLLR0"

ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

def safe_eval(expr: str) -> float:
    expr = expr.replace("×", "*").replace("÷", "/").replace(",", ".").strip()
    if not expr:
        raise ValueError("Ifoda bo‘sh.")
    if len(expr) > 200:
        raise ValueError("Ifoda juda uzun.")

    node = ast.parse(expr, mode="eval")

    def _eval(n):
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        if isinstance(n, ast.UnaryOp) and type(n.op) in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[type(n.op)](_eval(n.operand))
        if isinstance(n, ast.BinOp) and type(n.op) in ALLOWED_OPERATORS:
            left = _eval(n.left)
            right = _eval(n.right)
            if isinstance(n.op, ast.Div) and right == 0:
                raise ValueError("0 ga bo‘lib bo‘lmaydi.")
            return ALLOWED_OPERATORS[type(n.op)](left, right)
        raise ValueError("Faqat +, -, *, / va qavslar ruxsat.")

    return _eval(node)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 Kalkulyator bot!\n"
        "Misol yubor: 12*(3-1)/2\n"
        "Ruxsat: +  -  *  /  ( )"
    )

async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        result = safe_eval(text)
        if abs(result - round(result)) < 1e-12:
            out = str(int(round(result)))
        else:
            out = str(result)
        await update.message.reply_text(f"✅ Natija: {out}")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calc))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()

