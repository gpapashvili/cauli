from .models import TransactionTypes

def transaction_types(request):
    """Used to display transaction types in the navigation bar."""
    return {
        'transaction_types': TransactionTypes.objects.all()
    }
