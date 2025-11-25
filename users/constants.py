EMAIL_VERIFICATION_SUBJECT = "Verify Your Email - Edulance"

EMAIL_VERIFICATION_MESSAGE = """
Hello {username},

Thank you for registering with Edulance!

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
Edulance Team
"""



FORGOT_PASSWORD_SUBJECT = "Your Temporary Password - Edulance"

FORGOT_PASSWORD_MESSAGE = """
Hello {username},

You have requested a password reset for your Edulance account.

Your temporary password is: {temporary_password}

Please use this password to log in, and we strongly recommend changing it immediately after logging in.

Best regards,
The Edulance Team
"""