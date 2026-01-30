from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib import auth

from jobapp.models import *
from django_ckeditor_5.widgets import CKEditor5Widget


# Admin CRUD Forms
class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.RadioSelect)):
                self.fields[field].widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(self.fields[field].widget, forms.Select):
                self.fields[field].widget.attrs.update({'class': 'form-select'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-control'})


class JobForm(BootstrapFormMixin, forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['title'].label = "Job Title :"
        self.fields['location'].label = "Job Location :"
        self.fields['salary'].label = "Salary :"
        self.fields['description'].label = "Job Description :"
        self.fields['tags'].label = "Tags :"
        self.fields['last_date'].label = "Submission Deadline :"
        self.fields['company_name'].label = "Company Name :"
        self.fields['url'].label = "Website :"


        self.fields['title'].widget.attrs.update(
            {
                'placeholder': 'eg : Software Developer',
            }
        )        
        self.fields['location'].widget.attrs.update(
            {
                'placeholder': 'eg : Bangladesh',
            }
        )
        self.fields['salary'].widget.attrs.update(
            {
                'placeholder': '$800 - $1200',
            }
        )
        self.fields['tags'].widget.attrs.update(
            {
                'placeholder': 'Use comma separated. eg: Python, JavaScript ',
            }
        )                        
        self.fields['last_date'].widget.attrs.update(
            {
                'placeholder': 'YYYY-MM-DD ',
                'class': 'form-control datepicker',
                'type': 'text'
            }
        )
        self.fields['company_name'].widget.attrs.update(
            {
                'placeholder': 'Company Name',
            }
        )           
        self.fields['url'].widget.attrs.update(
            {
                'placeholder': 'https://example.com',
            }
        )    


    class Meta:
        model = Job

        fields = [
            "title",
            "location",
            "category",
            "salary",
            "description",
            "tags",
            "last_date",
            "company_name",
            "company_description",
            "url"
            ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'cols': 50, 'placeholder': 'Enter detailed job description...'}),
            'company_description': forms.Textarea(attrs={'rows': 4, 'cols': 50, 'placeholder': 'Enter company description...'}),
        }





    def clean_category(self):
        category = self.cleaned_data.get('category')

        if not category:
            raise forms.ValidationError("Category is required")
        return category

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or len(title.strip()) < 3:
            raise forms.ValidationError("Job title must be at least 3 characters long")
        return title.strip()

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if not location or len(location.strip()) < 2:
            raise forms.ValidationError("Location must be at least 2 characters long")
        return location.strip()

    def clean_salary(self):
        salary = self.cleaned_data.get('salary')
        if not salary or len(salary.strip()) < 1:
            raise forms.ValidationError("Salary is required")
        return salary.strip()

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if not company_name or len(company_name.strip()) < 2:
            raise forms.ValidationError("Company name must be at least 2 characters long")
        return company_name.strip()

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description or len(description.strip()) < 10:
            raise forms.ValidationError("Job description must be at least 10 characters long")
        return description.strip()


    def save(self, commit=True):
        job = super(JobForm, self).save(commit=False)
        if commit:
            
            job.save()
        return job




class JobApplyForm(forms.ModelForm):
    resume = forms.FileField(required=True, label="Upload Resume")
    class Meta:
        model = Applicant
        fields = ['job', 'resume']

class JobBookmarkForm(forms.ModelForm):
    class Meta:
        model = BookmarkJob
        fields = ['job']




class JobEditForm(BootstrapFormMixin, forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['title'].label = "Job Title :"
        self.fields['location'].label = "Job Location :"
        self.fields['salary'].label = "Salary :"
        self.fields['description'].label = "Job Description :"
        # self.fields['tags'].label = "Tags :"
        self.fields['last_date'].label = "Dead Line :"
        self.fields['company_name'].label = "Company Name :"
        self.fields['url'].label = "Website :"


        self.fields['title'].widget.attrs.update(
            {
                'placeholder': 'eg : Software Developer',
            }
        )        
        self.fields['location'].widget.attrs.update(
            {
                'placeholder': 'eg : Bangladesh',
            }
        )
        self.fields['salary'].widget.attrs.update(
            {
                'placeholder': '$800 - $1200',
            }
        )
        # self.fields['tags'].widget.attrs.update(
        #     {
        #         'placeholder': 'Use comma separated. eg: Python, JavaScript ',
        #     }
        # )                        
        self.fields['last_date'].widget.attrs.update(
            {
                'placeholder': 'YYYY-MM-DD ',
            }
        )        
        self.fields['company_name'].widget.attrs.update(
            {
                'placeholder': 'Company Name',
            }
        )           
        self.fields['url'].widget.attrs.update(
            {
                'placeholder': 'https://example.com',
            }
        )    

    
        last_date = forms.CharField(widget=forms.TextInput(attrs={
                    'placeholder': 'Service Name',
                    'class' : 'datetimepicker1'
                }))

    class Meta:
        model = Job

        fields = [
            "title",
            "location",
            "job_type",
            "category",
            "salary",
            "description",
            "last_date",
            "company_name",
            "company_description",
            "url"
            ]

    def clean_job_type(self):
        job_type = self.cleaned_data.get('job_type')

        if not job_type:
            raise forms.ValidationError("Job Type is required")
        return job_type

    def clean_category(self):
        category = self.cleaned_data.get('category')

        if not category:
            raise forms.ValidationError("Category is required")
        return category


    def save(self, commit=True):
        job = super(JobEditForm, self).save(commit=False)

        if commit:
            job.save()
        return job

class CourseForm(forms.ModelForm):
    marks_per_question = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        help_text="How many marks is each question worth? (1-10)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make total_marks read-only
        self.fields['total_marks'].widget.attrs['readonly'] = True
        self.fields['total_marks'].help_text = "Auto-calculated: Questions × Marks per question"

    def clean(self):
        cleaned_data = super().clean()
        question_number = cleaned_data.get('question_number')
        marks_per_question = cleaned_data.get('marks_per_question')

        if question_number and marks_per_question:
            # Auto-calculate total_marks
            cleaned_data['total_marks'] = question_number * marks_per_question
        else:
            raise forms.ValidationError("Both question number and marks per question are required.")

        return cleaned_data

    class Meta:
        model = Course
        fields = ['course_name', 'question_number', 'marks_per_question', 'total_marks']


class QuestionForm(forms.ModelForm):
    # this will show dropdown __str__ method course model is shown on html so override it
    # to_field_name this will fetch corresponding value  user_id present in course model and return it
    courseID = forms.ModelChoiceField(queryset=Course.objects.all(), empty_label="Course Name",
                                      to_field_name="id")

    class Meta:
        model = Question
        fields = ['marks', 'question', 'option1', 'option2', 'option3', 'option4', 'answer']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'cols': 50})
        }

class TeacherForm(forms.ModelForm):
    class Meta:
        model= Teacher
        fields=['address','mobile','profile_pic']

class StudentForm(forms.ModelForm):
    class Meta:
        model=Student
        fields=['address','mobile','profile_pic']


class AdminUserForm(BootstrapFormMixin, forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    password_confirm = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name', 'role', 'gender', 'is_active', 'is_staff']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password != password_confirm:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class AdminJobForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'job_type', 'category', 'salary',
                 'company_name', 'company_description', 'url', 'last_date', 'is_published', 'is_closed', 'user', 'tags']
        widgets = {
            'last_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 6}),
            'company_description': forms.Textarea(attrs={'rows': 4}),
        }


class AdminApplicantForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ['user', 'job', 'resume']


class AdminCategoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class AdminCourseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_name', 'question_number', 'marks_per_question', 'total_marks']

class AdminQuestionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Question
        fields = ['course', 'marks', 'question', 'option1', 'option2', 'option3', 'option4', 'answer']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'cols': 50})
        }

class AdminResultForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'exam', 'marks']

class AdminBookmarkForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = BookmarkJob
        fields = ['user', 'job']

class AdminStudentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Student
        fields = ['user', 'profile_pic', 'address', 'mobile']

class AdminTeacherForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['user', 'profile_pic', 'address', 'mobile', 'status', 'salary']

