from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def renderPdf(template, context = {}):
    t = get_template(template)
    send_data = t.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(send_data.encode("ISO-8859-1")), result)
    if not pdf.err:
        # print('Hapa nimefika')
        return HttpResponse(result.getvalue(), content_type = 'application/pdf')
    else:
        return None
