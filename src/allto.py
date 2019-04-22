class allto:
	def getDefaultEmail(answer):
		try:
			from_email = conf.get("from_email")
		except KeyError, Exception:
			from_email = u""
		return from_email

	def getContentType(answer, conttype):
		return answer.get("content_type").lower() == conttype.lower()

	def sendMail(mailinfo):
		sg = sendgrid.SendGridAPIClient(api_key=conf.get("api_key"))
		from_email = Email(mailinfo.get("from_email"))
		to_email = Email(mailinfo.get("to_email"))
		subject = mailinfo.get("subject").title()
		content_type = "text/plain" if mailinfo.get("content_type") == "text" else "text/html"
		content = Content(content_type, mailinfo.get("content"))
		mail = Mail(from_email, subject, to_email, content)
		response = sg.client.mail.send.post(request_body=mail.get())
		return response


	def log(string, color, font="slant", figlet=False):
		if colored:
			if not figlet:
				six.print_(colored(string, color))
			else:
				six.print_(colored(figlet_format(
					string, font=font), color))
		else:
			six.print_(string)	
			