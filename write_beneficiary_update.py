content = open('documents/models.py', 'r', encoding='utf-8').read()

addition = """

class BeneficiarySecurityQuestion(models.Model):
    \"\"\"
    Security questions a beneficiary must answer
    before accessing their assigned assets.
    Set by the user when assigning a beneficiary.
    \"\"\"
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='security_questions'
    )
    question    = models.CharField(max_length=255)
    answer      = models.CharField(max_length=255)
    created_at  = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Question for {self.beneficiary.name}"
"""

with open('documents/models.py', 'w', encoding='utf-8') as f:
    f.write(content + addition)

print('Done!')