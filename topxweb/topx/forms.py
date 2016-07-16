from django import forms

class importanciaForm(forms.Form):
    url = forms.CharField(label='url', max_length=200,
    	widget=forms.TextInput(attrs={'class': "input-lg"})
		)
    topx = forms.IntegerField(label='Top(X)',
    	widget=forms.TextInput(attrs={'class': "input-lg"})
    	)