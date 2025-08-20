from .models import TransactionTypes

def transaction_types(request):
    return {
        'transaction_types': TransactionTypes.objects.all()
    }
