# Vikas Mourya

## Submission checklist

- [x] Your submission follows best practices for [commit messages](https://chris.beams.io/posts/git-commit/) AND for [pull requests](https://github.community/t/best-practices-for-pull-requests/10195)
- [x] `Steps to run the project` AND a `documentation` have been included in a README.md file at root of your project.
- [x] No `binaries/compressed` files have been added
- [x] All pre-existing files in the repository have been removed
- [x] `Screenshots` have been added to the screenshots folder
- [x] All italicesed instructions under each submission heading inline, have been removed.
- [x] You understand that a submission here is publicly visible. 
- [x] You have not plagiarised, or blatently copied work; and this submission is your original work.

### Setup Instructions
1. Clone the repository
2. Create a virtual environment: `python -m venv env`
3. Activate the environment: `source env/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Start server: `python manage.py runserver`

## Briefly write about the project that you have submitted from the perspective of the user.
A Google Forms-like application that allows users to create, share and analyze form responses. Admins can create forms with different question types (text, dropdown, checkbox) while end users can submit responses anonymously. Both parties can view analytics for responses.

## Assumptions you have made for this project?
1. Forms are public and don't require authentication to submit responses
2. Maximum 100 questions per form
3. Questions can be reordered after creation
4. Analytics are calculated in real-time
5. Multiple submissions allowed from same user/IP

## Other information (like testing credentials)
No special credentials needed. Access admin interface at:
- URL: http://localhost:8000/admin
- Username: vickypedia
- Password: vik#1207

## Did you learn anything new while doing this assignment? Please explain.
1. Implemented drag-and-drop reordering using jQuery UI
2. Learned about Django form validation for dynamic fields
3. Explored analytics calculation and caching strategies
4. Improved understanding of Django template inheritance
5. Explored Django Rest Framework and implemented API driven as well as UI driven Django Application

## How much time did it take for you complete the project?
Approximately 25-30 hours including:
- Initial setup & planning: 3 hours
- Core functionality: 15 hours
- Testing & bug fixes: 5 hours
- Documentation: 2 hours

## If you had more time, what enhancements will you make?
1. Add support for more question types (date, file upload, ranking)
2. Implement response validation rules
3. Add export functionality for responses
4. Enable form templates/duplication
5. Add user authentication for form creators
6. Implement real-time analytics updates
7. Add form branching logic
8. Enable form response editing