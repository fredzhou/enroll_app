# Create your views here.
from django import forms
from django.shortcuts import render
from django.http import HttpResponse
from models import ContactModel
import subprocess
import ldap
import smtplib
from email.mime.text import MIMEText


SVNDATA = '/home/coach/svndata/'
HTTP_ADDRESS = 'http://10.140.90.27/ccc2013/svn/'
SENDER = 'feng-fred.zhou@nsn.com'

class ContactForm(forms.Form):
    BU_NAMES = (
            (u'RNC', u'Controller SW3'),
            (u'BTS', u'BTS'),
            (u'LTE', u'LTE'),
            (u'DX200', u'DX 200'),
            (u'MGW', u'MGW'),
            (u'others', u'others'),

    )
    business_unit = forms.ChoiceField(choices = BU_NAMES)
    nsn_intra_id = forms.CharField(label='NSN-INTRA name')
    employee_number = forms.IntegerField(label='Employee ID')
    #co_author_employee_num = forms.IntegerField(label='Co-Author\'s employee ID', required=False)

def _store_enrollment_info(authorForm):
    try:
        c = ContactModel.objects.get(nsn_intra_id = authorForm.cleaned_data['nsn_intra_id'])
        return False
    except ContactModel.DoesNotExist:
        c = ContactModel()
        c.business_unit =  authorForm.cleaned_data['business_unit']
        c.nsn_intra_id = authorForm.cleaned_data['nsn_intra_id']
        c.employee_number =  authorForm.cleaned_data['employee_number']
        c.save()
        return True


def _create_repository(nsn_intra_id):
    repos_name = SVNDATA + nsn_intra_id
    p = subprocess.Popen(['svnadmin', 'create', repos_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()


def _add_user_right_for_repository(nsn_intra_id):
    svn_access_config = SVNDATA + 'svn_path_access.conf'
    try:
        with open(svn_access_config,'a+') as f:
            f.write('[' +  nsn_intra_id + ':/]\n')
            f.write('@judges = rw\n')
            f.write(nsn_intra_id + ' = rw\n')
            f.write('* =\n')
    finally:
        f.close()

def _ldap_search(filterStr):
    l = ldap.initialize("ldap://10.135.55.17:389")
    l.simple_bind_s("", "")

    retrieve_attributes = None
    scope = ldap.SCOPE_SUBTREE
    base = ""

    result_id = l.search(base, scope, filterStr, retrieve_attributes)

    result_type, result_data = l.result(result_id, 0)

    return (result_type, result_data)


def _is_uid_employNumber_matched(nsn_intra_id, employee_number):
    filterStr = 'employeeNumber=' + str(employee_number)
    result_type, result_data = _ldap_search(filterStr)
    if result_type == ldap.RES_SEARCH_ENTRY:
        fetched_nsn_intra_id = result_data[0][1]['uid'][0]
        return fetched_nsn_intra_id == nsn_intra_id 
    else:
        return False

def _fetch_mail_addressd(nsn_intra_id):
    filterStr = 'uid=' + str(nsn_intra_id)
    result_type, result_data = _ldap_search(filterStr)

    if result_type == ldap.RES_SEARCH_ENTRY:
        return result_data[0][1]['mail'][0]
    else:
        return ''

def _notify_candidate(to, msg_body):
    msg = MIMEText(msg_body)

    msg['Subject'] = 'Congrats for successful enrollment to clean code contest!'
    msg['From'] =  SENDER
    msg['To'] = to

    s = smtplib.SMTP('localhost')
    s.sendmail(SENDER, [to], msg.as_string())
    s.quit()

def _post(request):
    authorForm = ContactForm(request.POST) # A form bound to the POST data
    if not authorForm.is_valid():
        return render(request, 'template/contact_form.html', {
                    'authorForm': authorForm,
                })

    nsn_intra_id = authorForm.cleaned_data['nsn_intra_id']
    if not _is_uid_employNumber_matched(nsn_intra_id, authorForm.cleaned_data['employee_number']):
        return render(request, 'template/account_error.html', {})

    repos_address = HTTP_ADDRESS + authorForm.cleaned_data['nsn_intra_id']
    repos_address_notification = 'Here comes the url for contest svn repository, Please login with your nsn-intra name and password ' + repos_address

    to_mail = _fetch_mail_addressd(nsn_intra_id)

    if not _store_enrollment_info(authorForm):
        _notify_candidate(to_mail, repos_address_notification)
        return render(request, 'template/user_existed.html', {'repos_address': repos_address})

    _create_repository(nsn_intra_id)
    _add_user_right_for_repository(nsn_intra_id)

    _notify_candidate(to_mail, repos_address_notification)

    return render(request, 'template/enroll_successful.html', {'repos_address': repos_address})

def enroll(request):
    if request.method == 'POST': # If the form has been submitted...
        html = _post(request)
        return html
    else:
        authorForm = ContactForm() # An unbound form

    return render(request, 'template/contact_form.html', {
                        'authorForm': authorForm,
                    })
