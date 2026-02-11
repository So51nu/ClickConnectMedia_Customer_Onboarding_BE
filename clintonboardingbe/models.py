from django.db import models

class CompanyProfile(models.Model):
    """
    Singleton: admin ek baar signature upload karega.
    """
    company_name = models.CharField(max_length=255, default="Click Connect Media Pvt. Ltd.")
    signature_image = models.ImageField(upload_to="company/signatures/", null=True, blank=True)
    stamp_image = models.ImageField(upload_to="company/stamps/", null=True, blank=True)
    def __str__(self):
        return self.company_name


class ClientApplication(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # Step 1: Org
    orgName = models.CharField(max_length=255)
    orgPAN = models.CharField(max_length=50)
    orgAddress = models.TextField()
    incorpNo = models.CharField(max_length=100, blank=True, default="")
    incorpDate = models.CharField(max_length=20, blank=True, default="")
    businessNature = models.CharField(max_length=255)
    gstNumber = models.CharField(max_length=100, blank=True, default="")
    billingAddress = models.TextField()
    tanNumber = models.CharField(max_length=100, blank=True, default="")
    orgEmail = models.CharField(max_length=255)
    orgWebsite = models.CharField(max_length=255, blank=True, default="")
    orgContact = models.CharField(max_length=50)
    orgAltContact = models.CharField(max_length=50, blank=True, default="")

    # Step 2: Auth signatory
    authName = models.CharField(max_length=255)
    authPAN = models.CharField(max_length=50)
    authDesignation = models.CharField(max_length=255)
    authDOB = models.CharField(max_length=20)
    authMobile = models.CharField(max_length=50)
    authEmail = models.CharField(max_length=255)
    authNationality = models.CharField(max_length=100)
    correspondenceAddress = models.TextField()
    authLetter = models.BooleanField(default=False)
    idProof = models.BooleanField(default=False)

    authPanFront = models.ImageField(upload_to="applications/auth_pan/", null=True, blank=True)
    authPanBack = models.ImageField(upload_to="applications/auth_pan/", null=True, blank=True)
    authAadhaarFront = models.ImageField(upload_to="applications/auth_aadhaar/", null=True, blank=True)
    authAadhaarBack = models.ImageField(upload_to="applications/auth_aadhaar/", null=True, blank=True)

    # Step 3: services (store as CSV)
    services_csv = models.TextField(blank=True, default="")

    # Step 4
    digitalRequirements = models.BooleanField(default=False)
    digitalNotes = models.BooleanField(default=False)

    # Step 5
    communicationCompliance = models.BooleanField(default=False)

    # Step 6
    termsAgreement = models.BooleanField(default=False)

    # Step 7 Undertaking
    applicantName = models.CharField(max_length=255)
    applicantDate = models.CharField(max_length=20)
    applicantSignatureFile = models.ImageField(upload_to="applications/signatures/", null=True, blank=True)

    companySignatory = models.CharField(max_length=255, blank=True, default="")
    companyDate = models.CharField(max_length=20, blank=True, default="")
    companySignatureFile = models.ImageField(upload_to="applications/signatures/", null=True, blank=True)

    def services_list(self):
        if not self.services_csv.strip():
            return []
        return [x.strip() for x in self.services_csv.split(",") if x.strip()]

    def __str__(self):
        return f"{self.orgName} - {self.created_at:%Y-%m-%d %H:%M}"
