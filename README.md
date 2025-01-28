# 📈 GitHub Trending Mailer

A sophisticated Python application that automatically tracks GitHub's trending repositories, generates AI-powered summaries, and delivers them directly to your inbox. Stay updated with the latest trends in the developer community without leaving your email!

## ✨ Features

- 🔄 **Daily Updates**: Automatically scrapes GitHub's trending page daily
- 🤖 **AI-Powered Summaries**: Uses Groq AI to generate:
  - Overall trend analysis
  - Individual repository summaries
  - Technical significance and impact assessments
- 📧 **Smart Email Delivery**:
  - Beautiful, responsive HTML emails
  - Clean and modern design
  - Works with both Outlook and SMTP
- 🎯 **Intelligent Analysis**:
  - Language and technology trends
  - Star counts and popularity metrics
  - Project significance and use cases

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- A Groq API key for AI summaries
- Email account (Outlook or SMTP-compatible)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/arastuthakur/github-trending-mailer.git
cd github-trending-mailer
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your credentials:
```env
GROQ_API_KEY=your_groq_api_key
EMAIL_USER=your_email@example.com
EMAIL_PASSWORD=your_email_password
```

## 🔧 Configuration

The application can be configured through environment variables in the `.env` file:

- `GROQ_API_KEY`: Your Groq API key for AI summaries
- `EMAIL_USER`: Your email address
- `EMAIL_PASSWORD`: Your email password/app password
- Additional SMTP settings can be configured in the code if needed

## 📝 Usage

1. Run the application:
```bash
python github_trending_mailer.py
```

2. The script will:
   - Fetch trending repositories from GitHub
   - Generate AI summaries using Groq
   - Create a beautifully formatted email
   - Send it to the configured email address
   - Save a local copy in the summaries directory

By default, the mailer runs daily at 9:00 AM and also runs once immediately when started.

## 📁 Project Structure

```
github-trending-mailer/
├── github_trending_mailer.py  # Main application file
├── requirements.txt           # Python dependencies
├── .env                      # Environment variables
├── README.md                 # This file
├── github_trending.log       # Application logs
└── summaries/               # Directory for saved HTML summaries
```

## 🛠️ Customization

You can customize various aspects of the application:

- Modify the number of repositories to track
- Adjust the email sending frequency
- Customize the email template
- Configure different email providers
- Adjust AI summary parameters

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Developer

Developed with 💻 by [Arastu Thakur](https://github.com/arastuthakur)

- GitHub: [@arastuthakur](https://github.com/arastuthakur)
- LinkedIn: [Arastu Thakur](https://linkedin.com/in/arastuthakur)
- Email: [arustuthakur@gmail.com](mailto:arustuthakur@gmail.com)

## 🙏 Acknowledgments

- GitHub for the trending repository data
- Groq for the AI summarization capabilities
- All the awesome open-source libraries used in this project 
