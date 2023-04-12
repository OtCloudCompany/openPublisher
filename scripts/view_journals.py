from journals.models import Journal


def run():
    journals = Journal.objects.all()

    for journal in journals:
        print(journal.pk, journal.abbreviation, journal.title)
