from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from .forms import ContactForm

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            # Professional HTML email body
            html_message = f"""
                <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Subject:</strong> {subject}</p>
                    <p><strong>Message:</strong></p>
                    <p style="margin-left:15px;">{message}</p>
                    <hr style="margin:20px 0; border: none; border-top: 1px solid #ccc;">
                    <p style="text-align:right; color:#2563eb; font-weight:bold;">
                        Thank you ❤️ TastyCart ♥️♥️
                    </p>
                </div>
            """

            send_mail(
                subject,
                "",  # leave plain text empty
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_US_EMAIL],
                fail_silently=False,
                html_message=html_message,  # ✅ send formatted HTML
            )

            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    return render(request, "contact/contact.html")