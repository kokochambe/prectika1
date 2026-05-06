from django import forms
from .models import TaskNotification, WorkOrder


class AssignTaskForm(forms.Form):
    """Форма для назначения задачи работнику"""
    worker = forms.ModelChoiceField(
        queryset=None,
        label='Исполнитель',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        label='Сообщение/Инструкция',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Введите инструкцию для исполнителя...'}),
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем только техников
        from accounts.models import User
        self.fields['worker'].queryset = User.objects.filter(role='technician', is_active=True)
        self.fields['worker'].label_from_instance = lambda obj: f"{obj.username} ({obj.get_role_display()})"


class CreateWorkOrderForm(forms.ModelForm):
    """Форма создания наряда-заказа с назначением исполнителя"""
    class Meta:
        model = WorkOrder
        fields = ['equipment', 'order_type', 'priority', 'assigned_user', 'description']
        widgets = {
            'equipment': forms.Select(attrs={'class': 'form-control'}),
            'order_type': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'assigned_user': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем только техников для назначения
        from accounts.models import User
        self.fields['assigned_user'].queryset = User.objects.filter(role='technician', is_active=True)
        self.fields['assigned_user'].label_from_instance = lambda obj: f"{obj.username} ({obj.get_role_display()})"
        self.fields['assigned_user'].required = False
        self.fields['assigned_user'].label = 'Назначить исполнителя (необязательно)'
