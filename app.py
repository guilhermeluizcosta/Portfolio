from flask import Flask, render_template, request, flash, redirect , url_for, send_from_directory
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('secret_key')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'guilhermelc10@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv('senha_email')
mail = Mail(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        assunto = request.form['assunto']
        mensagem = request.form['mensagem']

        if not nome or not telefone or not assunto or not mensagem:
            flash('Por favor, preencha todos os campos!', 'error')
            return redirect(url_for('home'))

        # Enviar email
        msg = Message(subject=f"Contato: {assunto}",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=['guilhermelc10@gmail.com'],
                      body=f"""
Nome: {nome}
E-mail:{email}
Telefone: {telefone}
Assunto: {assunto}

Mensagem:
{mensagem}
                      """)
        try:
            mail.send(msg)
            flash('Message sent successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred while sending the email{e}', 'error')

        return redirect(url_for('home'))

    return render_template('home.html')

@app.route('/download/<filename>')
def download_file(filename):
    directory = 'cv'
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == '__main__':
    app.run()