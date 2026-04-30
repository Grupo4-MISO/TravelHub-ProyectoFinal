from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

#Variables para enviar el correo
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'travelhub.reservations@gmail.com' 
SMTP_PASS = 'hkzu sqcg crdy gxmk'

class EmailHelper:
    @staticmethod
    def headerEmailMessage(body):
        #Creamos el mensaje de email
        message = MIMEMultipart('alternative')

        #Definimos el asunto, el remitente y el destinatario del email
        message['Subject'] = '!Tu reserva ha sido confirmada!'
        message['From'] = SMTP_USER
        message['To'] = body.get('cliente').get('email')

        print(f"Email a enviar: {message['To']}")

        return message
    
    @staticmethod
    def createEmailMessage(message, data):
        print(data)
        #Cuerpo del correo en formato HTML
        html = f"""\
        <html>
        <body style="margin:0; padding:0; background-color:#f4f6f8; font-family:Arial, sans-serif;">
            
            <table width="100%" bgcolor="#f4f6f8" cellpadding="0" cellspacing="0">
            <tr>
                <td align="center">
                
                <!-- Contenedor -->
                <table width="600" cellpadding="0" cellspacing="0" 
                        style="background:#ffffff; margin:40px 0; border-radius:10px; overflow:hidden;">
                    
                    <!-- Header -->
                    <tr>
                    <td style="padding:20px 30px;">
                        <h2 style="margin:0; color:#333;">¡Tu reserva ha sido confirmada! ✅</h2>
                    </td>
                    </tr>

                    <!-- Intro -->
                    <tr>
                    <td style="padding:0 30px 20px 30px; color:#555;">
                        <p>Gracias por reservar con nosotros.</p>
                        <p>Tu reserva ha sido confirmada exitosamente en la ciudad de {data['hospedaje']['ciudad']} en el país {data['hospedaje']['pais']}. A continuación, te proporcionamos los detalles:</p>
                    </td>
                    </tr>

                    <!-- Card Reserva -->
                    <tr>
                    <td style="padding:0 30px;">
                        <table width="100%" style="border:1px solid #e0e0e0; border-radius:8px; padding:15px;">
                            <tr>
                                <td>
                                    <strong>Código de reserva #{data['reserva']['codigo_reserva']}</strong>
                                </td>
                                <td align="right">
                                    <span style="background:#d4edda; color:#155724; padding:5px 10px; border-radius:20px; font-size:12px;">
                                        Confirmada
                                    </span>
                                </td>
                            </tr>

                            <tr>
                                <td colspan="2" style="padding-top:15px;">
                                    <table width="100%">
                                        <tr>
                                            <!-- Imagen -->
                                            <td width="40%">
                                                <img src="{data['hospedaje']['imagen']}" 
                                                    width="100%" 
                                                    style="border-radius:8px;">
                                            </td>

                                            <!-- Info -->
                                            <td style="padding-left:15px; vertical-align:top;">
                                                <h3 style="margin:0; color:#333;">
                                                    {data['hospedaje']['nombre']}
                                                </h3>
                                                <p style="margin:5px 0; color:#777; font-size:14px;">
                                                    {data['hospedaje']['direccion']}, {data['hospedaje']['ciudad']}
                                                </p>

                                                <p style="margin:10px 0 0 0; font-size:14px;">
                                                    <strong>Check-In:</strong> {data['reserva']['check_in']}
                                                </p>
                                                <p style="margin:5px 0; font-size:14px;">
                                                    <strong>Check-Out:</strong> {data['reserva']['check_out']}
                                                </p>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                    </tr>

                    <!-- Servicios -->
                    <tr>
                    <td style="padding:20px 30px;">
                        <table width="100%" style="border:1px solid #e0e0e0; border-radius:8px; padding:15px;">
                            <tr>
                                <td>
                                    <strong>Servicios incluidos</strong>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding-top:10px;">
                                    {"".join([
                                        f'<span style="display:inline-block; background:#f1f1f1; padding:8px 12px; margin:5px; border-radius:6px; font-size:13px;">{a["name"]}</span>'
                                        for a in data['hospedaje']['amenidades']
                                    ])}
                                </td>
                            </tr>
                        </table>
                    </td>
                    </tr>

                    <!-- Pago -->
                    <tr>
                    <td style="padding:0 30px 20px 30px;">
                        <table width="100%" style="border:1px solid #e0e0e0; border-radius:8px; padding:15px;">
                            <tr>
                                <td>
                                    <strong>Costo total de la estadía:</strong>
                                </td>
                                <td align="right" style="font-size:20px; color:#0d6efd;">
                                    $ {float(data['reserva']['tarifa_total']):.2f} {data['reserva']['currency']}
                                </td>
                            </tr>
                        </table>
                    </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                    <td style="text-align:center; padding:20px; color:#777; font-size:12px;">
                        <p>¡Te deseamos un excelente viaje!</p>
                        <p>Avenida del Turismo. Bogotá, Colombia</p>
                        <p>
                            Soporte | Preguntas frecuentes | Contactar
                        </p>
                        <p style="font-size:11px; color:#aaa;">
                            Esta es una notificación automática, por favor no respondas este correo.
                        </p>
                    </td>
                    </tr>

                </table>
                </td>
            </tr>
            </table>
        </body>
        </html>
        """

        message.attach(MIMEText(html, 'html'))
        return message

    @staticmethod
    def sendEmail(message):
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout = 30) as server:
                server.set_debuglevel(1)
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, message["To"], message.as_string())

        except Exception as e:
            return f'Error sending email: {str(e)}'