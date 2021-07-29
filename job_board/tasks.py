from django.core.mail import EmailMultiAlternatives


def send_otp(otp, email_address):
    email = EmailMultiAlternatives(subject='Mediusware Job - Password Reset')
    html_content = f'<h1>Mediusware Ltd</h1> ' \
                   f'<p>Use the following OTP to complete your Sign Up procedures. OTP is valid for 5 minutes</p>' \
                   f'<br>' \
                   f'{otp}' \
                   f'<hr>' \
                   f'<br>' \
                   f'<br>' \
                   f'Regards,' \
                   f'Mediusware Job'
    email.attach_alternative(html_content, 'text/html')
    email.to = [email_address]
    email.send()
