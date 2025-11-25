from django.core.signing import TimestampSigner, SignatureExpired, BadSignature

import secrets
import string

class EmailVerificationTokenGenerator:
    def __init__(self, salt="email-verification"):
        self.salt = salt
        self.signer = TimestampSigner(salt=self.salt)

    def generate_token(self, user):
        value = f"{user.id}:{user.email}"
        return self.signer.sign(value)

    def verify_token(self, token, max_age=86400):
        try:
            value = self.signer.unsign(token, max_age=max_age)

            user_id, email = value.split(":", 1)
            return user_id, email

        except SignatureExpired:
            raise SignatureExpired("Verification link has expired")
        except BadSignature:
            raise BadSignature("Invalid verification token")
        except (ValueError, AttributeError):
            raise BadSignature("Malformed verification token")


email_token_generator = EmailVerificationTokenGenerator()


def generate_verification_token(user):
    return email_token_generator.generate_token(user)


def verify_verification_token(token, max_age=86400):
    return email_token_generator.verify_token(token, max_age=max_age)




def generate_temporary_password(length=8):
    """
    Generate a secure temporary password.
    Contains uppercase, lowercase, digits, and special characters.
    """
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*"
    
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]
    
    all_characters = uppercase + lowercase + digits + special
    password += [secrets.choice(all_characters) for _ in range(length)]
    
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)
