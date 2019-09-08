# Generated by Django 2.1.10 on 2019-09-08 09:18

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('surname', models.CharField(blank=True, max_length=255, null=True, verbose_name='Bucque')),
                ('family', models.CharField(blank=True, max_length=255, null=True, verbose_name="Fam'ss")),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Solde')),
                ('virtual_balance', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Solde prévisionnel')),
                ('year', models.IntegerField(blank=True, choices=[(1953, 1953), (1954, 1954), (1955, 1955), (1956, 1956), (1957, 1957), (1958, 1958), (1959, 1959), (1960, 1960), (1961, 1961), (1962, 1962), (1963, 1963), (1964, 1964), (1965, 1965), (1966, 1966), (1967, 1967), (1968, 1968), (1969, 1969), (1970, 1970), (1971, 1971), (1972, 1972), (1973, 1973), (1974, 1974), (1975, 1975), (1976, 1976), (1977, 1977), (1978, 1978), (1979, 1979), (1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983), (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019)], null=True, verbose_name="Prom'ss")),
                ('campus', models.CharField(blank=True, choices=[('ME', 'Me'), ('AN', 'An'), ('CH', 'Ch'), ('BO', 'Bo'), ('LI', 'Li'), ('CL', 'Cl'), ('KA', 'Ka'), ('KIN', 'Kin')], max_length=3, null=True, verbose_name="Tabagn'ss")),
                ('phone', models.CharField(blank=True, max_length=255, null=True, validators=[django.core.validators.RegexValidator('^0[0-9]{9}$', 'Le numéro doit être\n                                                        du type\n                                                        0123456789')], verbose_name='Numéro de téléphone')),
                ('avatar', models.ImageField(blank=True, default=None, null=True, upload_to='img/avatars/', verbose_name='Avatar')),
                ('theme', models.CharField(blank=True, choices=[('light', 'Light'), ('dark', 'Dark'), ('birse', 'Birse')], max_length=15, null=True, verbose_name='Préférence de theme graphique')),
                ('jwt_iat', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Jwt iat')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'permissions': (('manage_presidents_group', 'Can manage presidents group'), ('manage_vice_presidents_group', 'Can manage vice presidents group'), ('manage_treasurers_group', 'Can manage treasurers group'), ('manage_members_group', 'Can manage members group'), ('manage_externals_group', 'Can manage externals group'), ('advanced_view_user', 'Can view advanced data on user')),
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
