# Morpheus

## Overview

Morpheus is a Django-based application that allows users to create and manage dynamic forms with ease. It provides a user-friendly interface for building forms, handling validations, and managing form submissions.

## Features

- **Dynamic Form Creation**: Easily create and customize forms without writing code.
- **Validation Support**: Built-in validation mechanisms to ensure data integrity.
- **Admin Interface**: Manage forms and submissions through a comprehensive admin panel.
- **Responsive Design**: Optimized for various devices and screen sizes.

## Setup Instructions

### Prerequisites

- **Python 3.12**
- **pip**
- **virtualenv**

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/Formbuilder.git
   cd Formbuilder

2. **Create a Virtual Environment**

```bash 
python3.12 -m venv myenv
source myenv/bin/activate
```

3. **Install Dependencies**
```
pip install -r requirements.txt
```
4. **settings.py**

```
DEBUG = True
```
5. Run Migrations
```
python manage.py migrate
```

6. Start Development Server
```
python manage.py runserver
```

# Usage Guide
## Admin Interface
Access the Django admin interface to manage forms and submissions.

1. *Create a Superuser*
```bash
python manage.py createsuperuser
```
2. *Login to Admin*
Navigate to http://localhost:8000/admin/ and log in with your superuser credentials.

3. *Manage Forms*
- *Add New Form*: Create new forms by defining fields and validations.
- *Edit Forms*: Modify existing forms as needed.
- *View Submissions*: Review and manage form submissions.