from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

#Variables para enviar el correo
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'travelhub.reservations@gmail.com' 
SMTP_PASS = 'kjyx rzlf ccli rqsj'

class EmailHelper:
    @staticmethod
    def headerEmailMessage(body):
        #Creamos el mensaje de email
        message = MIMEMultipart('alternative')

        #Definimos el asunto, el remitente y el destinatario del email
        message['Subject'] = 'Reserva Confirmada'
        message['From'] = SMTP_USER
        message['To'] = body.get('email')

        return message
    
    @staticmethod
    def createEmailMessage(message):
        #Creamos el cuerpo del mensaje de email
        html = f"""\
        <html>
        <body style="margin:0; padding:0; background-color:#f4f6f8; font-family:Arial, sans-serif;">
            
            <table width="100%" bgcolor="#f4f6f8" cellpadding="0" cellspacing="0">
            <tr>
                <td align="center">
                
                <!-- Contenedor -->
                <table width="600" cellpadding="0" cellspacing="0" 
                        style="background:#ffffff; margin:40px 0; border-radius:8px; overflow:hidden;">
                    
                    <!-- Header -->
                    <tr>
                    <td style="background:#0d6efd; padding:20px; text-align:center; color:white;">
                        <h1 style="margin:0; font-size:24px;">TravelHub ✈️</h1>
                    </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                    <td style="padding:30px; color:#333;">
                        <h2 style="margin-top:0;">Hola 👋</h2>
                        <p style="line-height:1.6;">
                        Tu reserva ha sido confirmada exitosamente. ¡Gracias por elegir TravelHub para tus aventuras de viaje! 🌍✈️
                        </p>

                        <p style="font-size:12px; color:#888;">
                        Si no solicitaste este correo, puedes ignorarlo.
                        </p>
                    </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                    <td style="background:#f1f1f1; padding:15px; text-align:center; font-size:12px; color:#777;">
                        © 2026 TravelHub. Todos los derechos reservados.
                    </td>
                    </tr>
                </table>
                </td>
            </tr>
            </table>
        </body>
        </html>
        """

        #Adjuntamos el cuerpo del mensaje al email
        message.attach(MIMEText(html, 'html'))

        return message

    @staticmethod
    def sendEmail(message):
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, message["To"], message.as_string())

        except Exception as e:
            return f'Error sending email: {str(e)}'