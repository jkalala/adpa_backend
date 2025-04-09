from django.db import models

class Member(models.Model):
    COUNTRY_CHOICES = [
        ('Angola', 'Angola'),
        ('South Africa', 'South Africa'),
        ('Zimbabwe', 'Zimbabwe'),
        ('Namibia', 'Namibia'),
        ('Tanzania', 'Tanzania'),
        ('Ghana', 'Ghana'),
        ('Guinea', 'Guinea'),
        ('DRC', 'DR Congo'),
        ('Congo', 'Republic of Congo'),
        ('Togo', 'Togo'),
        ('Central African Republic', 'Central African Republic'),
        ('Cameroon', 'Cameroon'),
        ('Côte d\'Ivoire', 'Côte d\'Ivoire'),
        ('Sierra Leone', 'Sierra Leone'),
        ('Liberia', 'Liberia'),
        ('Gabon', 'Gabon'),
        ('Algeria', 'Algeria'),
        ('Mali', 'Mali'),
        ('Mozambique', 'Mozambique'),
        ('Russia', 'Russia'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Observer', 'Observer'),
    ]
    
    TIER_CHOICES = [
        ('Founding', 'Founding'),
        ('Full', 'Full'),
        ('Associate', 'Associate'),
        ('Observer', 'Observer'),
    ]
    
    PAYMENT_CHOICES = [
        ('Current', 'Current'),
        ('Pending', 'Pending'),
        ('Overdue', 'Overdue'),
        ('Not Applicable', 'Not Applicable'),
    ]

    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES, unique=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    since = models.IntegerField()
    tier = models.CharField(max_length=15, choices=TIER_CHOICES)
    payment_status = models.CharField(max_length=15, choices=PAYMENT_CHOICES)
    representative = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.country

class Project(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Planning', 'Planning'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    countries = models.CharField(max_length=500)  # Comma-separated countries
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    progress = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    image_url = models.URLField(blank=True)
    implementing_agency = models.CharField(max_length=200, blank=True)

    def get_countries_list(self):
        """Returns countries as a list"""
        return [c.strip() for c in self.countries.split(',') if c.strip()]

    def set_countries(self, country_list):
        """Sets countries from a list"""
        self.countries = ','.join(str(c) for c in country_list)

    def __str__(self):
        return self.name

class Document(models.Model):
    CATEGORY_CHOICES = [
        ('governance', 'Governance'),
        ('membership', 'Membership'),
        ('reports', 'Reports'),
        ('templates', 'Templates'),
        ('financial', 'Financial'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    file_type = models.CharField(max_length=10)
    file_size = models.CharField(max_length=20)
    upload_date = models.DateTimeField(auto_now_add=True)
    download_count = models.IntegerField(default=0)
    file_url = models.URLField()
    restricted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('meeting', 'Meeting'),
        ('workshop', 'Workshop'),
        ('deadline', 'Deadline'),
        ('conference', 'Conference'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    virtual_link = models.URLField(blank=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title