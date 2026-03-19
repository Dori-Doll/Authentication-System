from email.mime import text
from tkinter import *
from tkinter import _setit
from function import enter

def showFrame(frame):
        frame.tkraise()

def lock_login_inputs():
	log_login_entry.config(state="disabled")
	log_pass_entry.config(state="disabled")
	log_btn.config(state="disabled")

def unlock_login_inputs():
	enter.reset_lock_state()
	log_login_entry.config(state="normal")
	log_pass_entry.config(state="normal")
	log_btn.config(state="normal")
	log_pass_entry.delete(0, END)
	log_msg_label.config(text="Можна спробувати ще раз.", fg="#1f5f8b")

def on_registration(username, password):
    if not username or not password:
        reg_msg_label.config(text="Логін або пароль не введено.")
        return
    elif len(password) < 4:
        reg_msg_label.config(text="Пароль має містити щонайменше 4 символи.")
        return
    elif enter._is_username_available(username):
        reg_login_entry.config(state="disabled")
        reg_pass_entry.config(state="disabled")
        reg_btn.config(state="disabled")
        open_registration_window()
    else:
        reg_msg_label.config(text="Цей логін вже зайнятий")
        return

def reset_registration_form():
	reg_login_entry.config(state="normal")
	reg_pass_entry.config(state="normal")
	reg_btn.config(state="normal")
	reg_login_entry.delete(0, END)
	reg_pass_entry.delete(0, END)
	reg_msg_label.config(text="")

def center_window(target_window, width, height):
	screen_width = target_window.winfo_screenwidth()
	screen_height = target_window.winfo_screenheight()
	x_coord = int((screen_width / 2) - (width / 2))
	y_coord = int((screen_height / 2) - (height / 2))
	target_window.geometry(f"{width}x{height}+{x_coord}+{y_coord}")
	
def select_dob_with_sequential_modals(parent_window):

	def open_choice_dialog(title, options, columns=4):
		selected_value = {"value": None}
		dialog = Toplevel(parent_window)
		dialog.title(title)
		dialog.configure(bg="#f8fbff")
		dialog.resizable(False, False)
		dialog.transient(parent_window)
		dialog.grab_set()

		frame = Frame(dialog, bg="#f8fbff")
		frame.pack(padx=16, pady=14)

		for idx, option in enumerate(options):
			button = Button(
				frame,
				text=str(option),
				font=("Arial", 11),
				width=10,
				command=lambda value=option: (selected_value.__setitem__("value", value), dialog.destroy())
			)
			button.grid(row=idx // columns, column=idx % columns, padx=4, pady=4)

		cancel_button = Button(
			dialog,
			text="Скасувати",
			font=("Arial", 10, "bold"),
			bg="#8a8f98",
			fg="white",
			command=dialog.destroy
		)
		cancel_button.pack(pady=(0, 10))

		dialog.update_idletasks()
		center_window(dialog, dialog.winfo_reqwidth(), dialog.winfo_reqheight())
		parent_window.wait_window(dialog)
		return selected_value["value"]

	years = enter.get_modal_birth_year_options()
	selected_year = open_choice_dialog("Оберіть Рік", years, columns=5)
	if selected_year is None:
		return None
	selected_year = str(selected_year)

	months = enter.get_modal_birth_month_options(selected_year)
	selected_month = open_choice_dialog("Оберіть Місяць", months, columns=4)
	if selected_month is None:
		return None
	selected_month = str(selected_month)

	days = enter.get_modal_birth_day_options(selected_year, selected_month)
	selected_day = open_choice_dialog("Оберіть День", days, columns=6)
	if selected_day is None:
		return None

	return enter.build_modal_birth_selection(selected_day, selected_month, selected_year)

def open_registration_window():
	registration_window = Toplevel()
	registration_window.title("РЕЄСТРАЦІЯ")
	registration_window.configure(bg="#fafafa")
	registration_window.resizable(False, False)
	center_window(registration_window, 760, 560)

	header_frame = Frame(registration_window, bg="#cac8c8", height=80)
	header_frame.pack(fill="x")

	header = Label(
		header_frame,
		text="Створення нового акаунта",
		font=("Arial", 24, "bold"),
		bg="#cac8c8"
	)
	header.pack(pady=(18, 10))

	form_frame = Frame(registration_window, bg="#cac8c8", bd=1, relief="solid")
	form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

	first_name_var = StringVar()
	last_name_var = StringVar()
	father_name_var = StringVar()
	birth_place_var = StringVar()
	birth_year_var = StringVar(value="")
	birth_month_var = StringVar(value="")
	birth_day_var = StringVar(value="")
	birth_date_display_var = StringVar(value="Не обрано")
	birth_date_selected = {"value": False}
	birth_place_selected = {"value": False}
	sex_options = enter.get_sex_options_display()
	sex_var = StringVar(value=sex_options[0] if sex_options else "")
	family_options = enter.get_family_status_options_display(sex_var.get())
	family_status_var = StringVar(value=family_options[0] if family_options else "")
	penalty_status_var = StringVar()

	row = 0

	def add_labeled_entry(label_text, text_var, show=None):
		nonlocal row
		label = Label(form_frame, text=label_text, font=("Arial", 12, "bold"), bg="#cac8c8", anchor="w")
		label.grid(row=row, column=0, sticky="w", padx=(16, 10), pady=(10, 4))
		entry = Entry(form_frame, textvariable=text_var, font=("Arial", 12), width=36, show=show)
		entry.grid(row=row, column=1, sticky="w", padx=(0, 16), pady=(10, 4))
		row += 1
		return entry

	add_labeled_entry("Ім'я", first_name_var)
	add_labeled_entry("Прізвище", last_name_var)
	add_labeled_entry("По батькові", father_name_var)

	birth_date_label = Label(form_frame, text="Дата народження", font=("Arial", 12, "bold"), bg="#cac8c8", anchor="w")
	birth_date_label.grid(row=row, column=0, sticky="w", padx=(16, 10), pady=(10, 4))
	birth_date_frame = Frame(form_frame, bg="#ffffff")
	birth_date_frame.grid(row=row, column=1, sticky="w", padx=(0, 16), pady=(10, 4))

	birth_date_value_label = Label(
		birth_date_frame,
		textvariable=birth_date_display_var,
		font=("Arial", 11, "bold"),
		bg="#ffffff",
		fg="#1f2a35",
		width=14,
		anchor="w"
	)
	birth_date_value_label.pack(side="left", padx=(0, 8))

	def choose_birth_date():
		selection = select_dob_with_sequential_modals(registration_window)
		if selection is None:
			return
		birth_day_var.set(selection["day"])
		birth_month_var.set(selection["month"])
		birth_year_var.set(selection["year"])
		birth_date_display_var.set(selection["display"])
		birth_date_selected["value"] = True

	birth_date_button = Button(
		birth_date_frame,
		text="ОБРАТИ",
		font=("Arial", 10, "bold"),
		bg="#1f5f8b",
		fg="white",
		activebackground="#2b6f9f",
		activeforeground="white",
		command=choose_birth_date
	)
	birth_date_button.pack(side="left")
	row += 1

	birth_place_label = Label(form_frame, text="Місце народження", font=("Arial", 12, "bold"), bg="#cac8c8", anchor="w")
	birth_place_label.grid(row=row, column=0, sticky="w", padx=(16, 10), pady=(10, 4))
	birth_place_entry = Entry(form_frame, textvariable=birth_place_var, font=("Arial", 12), width=36)
	birth_place_entry.grid(row=row, column=1, sticky="w", padx=(0, 16), pady=(10, 4))
	row += 1

	suggestions_listbox = Listbox(form_frame, font=("Arial", 11), height=6, width=45)
	suggestions_listbox.grid(row=row, column=1, sticky="w", padx=(0, 16), pady=(0, 6))
	suggestions_listbox.grid_remove()
	row += 1

	sex_label = Label(form_frame, text="Стать", font=("Arial", 12, "bold"), bg="#cac8c8", anchor="w")
	sex_label.grid(row=row, column=0, sticky="w", padx=(16, 10), pady=(10, 4))
	sex_menu = OptionMenu(form_frame, sex_var, *sex_options)
	sex_menu.config(font=("Arial", 11), width=18)
	sex_menu.grid(row=row, column=1, sticky="w", padx=(0, 16), pady=(10, 4))
	row += 1

	family_label = Label(form_frame, text="Сімейний стан", font=("Arial", 12, "bold"), bg="#cac8c8", anchor="w")
	family_label.grid(row=row, column=0, sticky="w", padx=(16, 10), pady=(10, 4))
	family_menu = OptionMenu(form_frame, family_status_var, *(family_options or [""]))
	family_menu.config(font=("Arial", 11), width=18)
	family_menu.grid(row=row, column=1, sticky="w", padx=(0, 16), pady=(10, 4))
	row += 1

	add_labeled_entry("Штрафи (необов'язково)", penalty_status_var)

	status_label = Label(form_frame, text="", font=("Arial", 11, "bold"), bg="#cac8c8", fg="#b22222")
	status_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=16, pady=(10, 4))
	row += 1

	def refresh_family_options(*_args):
		options = enter.get_family_status_options_display(sex_var.get())
		menu = family_menu["menu"]
		menu.delete(0, "end")
		for option in options:
			menu.add_command(label=option, command=_setit(family_status_var, option))
		if options:
			family_status_var.set(options[0])
		else:
			family_status_var.set("")

	def update_locality_suggestions(*_args):
		birth_place_selected["value"] = False
		query = birth_place_var.get().strip()
		if len(query) < 2:
			suggestions_listbox.grid_remove()
			suggestions_listbox.delete(0, END)
			return

		suggestions = enter.get_locality_suggestions(query, limit=20)
		suggestions_listbox.delete(0, END)
		for locality in suggestions:
			suggestions_listbox.insert(END, locality)

		if suggestions:
			suggestions_listbox.grid()
		else:
			suggestions_listbox.grid_remove()

	def select_suggestion(_event=None):
		if not suggestions_listbox.curselection():
			return
		selected_value = suggestions_listbox.get(suggestions_listbox.curselection()[0])
		birth_place_var.set(selected_value)
		birth_place_selected["value"] = True
		suggestions_listbox.grid_remove()

	def submit_registration():
		if not birth_date_selected["value"]:
			status_label.config(text="Оберіть дату народження.", fg="#b22222")
			return

		registration_data = {
			"username": reg_login_entry.get(),
			"password": reg_pass_entry.get(),
			"first_name": first_name_var.get(),
			"last_name": last_name_var.get(),
			"father_name": father_name_var.get(),
			"birth_day": birth_day_var.get(),
			"birth_month": birth_month_var.get(),
			"birth_year": birth_year_var.get(),
			"birth_place": birth_place_var.get(),
			"birth_place_selected": birth_place_selected["value"],
			"sex_display": sex_var.get(),
			"family_status_display": family_status_var.get(),
			"penalty_status": penalty_status_var.get(),
		}

		result = enter.register_new_user(registration_data)
		if result["ok"]:
			status_label.config(text=result["message"], fg="#1f7a1f")
			registration_window.after(1200, registration_window.destroy)
			handle_login(registration_data["username"], registration_data["password"])
		else:
			status_label.config(text=result["message"], fg="#b22222")
	birth_place_var.trace_add("write", update_locality_suggestions)
	sex_var.trace_add("write", refresh_family_options)
	suggestions_listbox.bind("<<ListboxSelect>>", select_suggestion)
	suggestions_listbox.bind("<Double-Button-1>", select_suggestion)
	birth_place_entry.bind("<Down>", lambda _e: suggestions_listbox.focus_set() if suggestions_listbox.size() else None)

	button_frame = Frame(form_frame, bg="#cac8c8")
	button_frame.grid(row=row, column=0, columnspan=2, pady=(12, 16))

	submit_button = Button(
		button_frame,
		text="ЗАРЕЄСТРУВАТИСЯ",
		font=("Arial", 12, "bold"),
		bg="#2e8b57",
		fg="white",
		activebackground="#3aa86b",
		activeforeground="white",
		width=18,
		command=submit_registration
	)
	submit_button.pack(side="left", padx=8)

	cancel_button = Button(
		button_frame,
		text="СКАСУВАТИ",
		font=("Arial", 12, "bold"),
		bg="#8a8f98",
		fg="white",
		activebackground="#9aa0aa",
		activeforeground="white",
		width=12,
		command=lambda: [registration_window.destroy(), reset_registration_form()]
	)
	cancel_button.pack(side="left", padx=8)

	registration_window.protocol("WM_DELETE_WINDOW", lambda: [registration_window.destroy(), reset_registration_form()])


	form_frame.grid_columnconfigure(1, weight=1)

def handle_login(username, password):
	login_result = enter.process_login_attempt(username, password)

	if login_result["ok"]:
		authenticated_session["user"] = login_result["user"]
		authenticated_session["is_admin"] = login_result["is_admin"]
		root.destroy()
		return

	log_pass_entry.delete(0, END)
	log_msg_label.config(text=login_result["message"])

	if login_result["locked"]:
		lock_login_inputs()
		root.after(login_result["retry_ms"], unlock_login_inputs)

def open_admin_window(admin_user):
	admin_window = Tk()
	admin_window.title("ПАНЕЛЬ АДМІНА")
	admin_window.configure(bg="#fafafa")
	admin_window.resizable(False, False)
	center_window(admin_window, 980, 650)

	header_frame = Frame(admin_window, bg="#cac8c8", height=84)
	header_frame.pack(fill="x")

	header_title = Label(
		header_frame,
		text=f"Панель Адміністратора: {admin_user.get('first_name', 'admin')}",
		font=("Arial", 24, "bold"),
		bg="#cac8c8"
	)
	header_title.pack(pady=18)

	container = Frame(admin_window, bg="#cac8c8")
	container.pack(fill="both", expand=True, padx=18, pady=14)

	canvas = Canvas(container, bg="#fafafa", highlightthickness=0)
	scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
	scrollable_frame = Frame(canvas, bg="#fafafa")

	scrollable_frame.bind(
		"<Configure>",
		lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
	)

	canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
	canvas.configure(yscrollcommand=scrollbar.set)

	def _on_mousewheel(event):
		canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

	def _on_linux_scroll_up(_event):
		canvas.yview_scroll(-1, "units")

	def _on_linux_scroll_down(_event):
		canvas.yview_scroll(1, "units")

	admin_window.bind_all("<MouseWheel>", _on_mousewheel)
	admin_window.bind_all("<Button-4>", _on_linux_scroll_up)
	admin_window.bind_all("<Button-5>", _on_linux_scroll_down)

	canvas.pack(side="left", fill="both", expand=True)
	scrollbar.pack(side="right", fill="y")

	for card in enter.build_admin_cards_data():
		user_card = Frame(scrollable_frame, bg="#cac8c8", bd=1, relief="solid")
		user_card.pack(fill="x", pady=8, padx=4)

		card_header = Label(
			user_card,
			text=card["title"],
			font=("Arial", 13, "bold"),
			bg="#0c151b",
			fg="white",
			anchor="w",
			padx=12,
			pady=7
		)
		card_header.pack(fill="x")

		body_frame = Frame(user_card, bg="#cac8c8")
		body_frame.pack(fill="x", padx=12, pady=10)

		for row_index, (label_text, value_text) in enumerate(card["rows"]):
			field_label = Label(
				body_frame,
				text=f"{label_text}:",
				font=("Arial", 11, "bold"),
				bg="#cac8c8",
				anchor="w"
			)
			field_label.grid(row=row_index, column=0, sticky="w", pady=3, padx=(0, 8))

			value_label = Label(
				body_frame,
				text=value_text,
				font=("Arial", 11),
				bg="#cac8c8",
				anchor="w",
				justify="left",
				wraplength=630
			)
			value_label.grid(row=row_index, column=1, sticky="w", pady=3)

		body_frame.grid_columnconfigure(1, weight=1)

	def _close_admin_window():
		admin_window.unbind_all("<MouseWheel>")
		admin_window.unbind_all("<Button-4>")
		admin_window.unbind_all("<Button-5>")
		admin_window.destroy()

	admin_window.protocol("WM_DELETE_WINDOW", _close_admin_window)

	close_button = Button(
		admin_window,
		text="ВИЙТИ",
		font=("MS Trebuchet", 12, "bold"),
		bg="#c0392b",
		fg="white",
		activebackground="#d35445",
		activeforeground="white",
		width=14,
		command=_close_admin_window
	)
	close_button.pack(pady=(0, 14))

	admin_window.mainloop()

def open_profile_window(user):
	profile_window = Tk()
	profile_window.title(f"ОСОБИСТИЙ КАБІНЕТ: {user['username']}")
	profile_window.configure(bg="#fafafa")
	profile_window.resizable(False, False)
	center_window(profile_window, 700, 520)

	header_frame = Frame(profile_window, bg="#cac8c8", height=90)
	header_frame.pack(fill="x")

	header_title = Label(
		header_frame,
		text=f"Вітаємо, {enter.get_user_header_name(user)}",
		font=("Arial", 24, "bold"),
		bg="#cac8c8"
	)
	header_title.pack(pady=(16, 0))

	header_subtitle = Label(
		header_frame,
		text="Ваші персональні дані",
		font=("Arial", 12),
		bg="#cac8c8"
	)
	header_subtitle.pack(pady=(4, 14))

	content_frame = Frame(profile_window, bg="#cac8c8", bd=1, relief="solid")
	content_frame.pack(fill="both", expand=True, padx=20, pady=16)

	for row_index, (label_text, value_text) in enumerate(enter.build_user_profile_rows(user)):
		field_label = Label(
			content_frame,
			text=f"{label_text}:",
			font=("Arial", 12, "bold"),
			bg="#cac8c8",
			anchor="w"
		)
		field_label.grid(row=row_index, column=0, sticky="w", padx=(16, 10), pady=8)

		value_label = Label(
			content_frame,
			text=value_text,
			font=("Arial", 12),
			bg="#cac8c8",
			anchor="w",
			justify="left",
			wraplength=430
		)
		value_label.grid(row=row_index, column=1, sticky="w", padx=(0, 16), pady=8)

	content_frame.grid_columnconfigure(1, weight=1)

	close_button = Button(
		profile_window,
		text="ВИЙТИ",
		font=("MS Trebuchet", 12, "bold"),
		bg="#c0392b",
		fg="white",
		activebackground="#d35445",
		activeforeground="white",
		width=14,
		command=profile_window.destroy
	)
	close_button.pack(pady=(0, 14))

	profile_window.mainloop()
        
authenticated_session = {"user": None, "is_admin": False}

root = Tk()

root['bg'] = '#fafafa'
root.title('Authorization System')
center_window(root, 250, 350)

root.resizable(width=False, height=False)

canvas = Canvas(root)
canvas.pack(fill=BOTH, expand=True)

frame_main = Frame(root, bg="#cac8c8")
frame_main.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

frame_reg = Frame(root, bg="#cac8c8")
frame_reg.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

frame_log = Frame(root, bg="#cac8c8")
frame_log.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)

for frame in (frame_main, frame_log):

    showFrame(frame_main)

    #main frame
    btn_reg = Button(frame_main, text="Зареєструватися", bg="#d9d9d9", command=lambda: showFrame(frame_reg))
    btn_reg.place(relx=0.5, rely=0.4, anchor=CENTER)

    btn_log = Button(frame_main, text="Увійти", bg="#d9d9d9", command=lambda: showFrame(frame_log))
    btn_log.place(relx=0.5, rely=0.6, anchor=CENTER)

    #registration frame
    return_btn = Button(frame_reg, text="<-", bg="#d9d9d9", command=lambda: showFrame(frame_main))
    return_btn.place(relx=0.1, rely=0.1, anchor=CENTER)

    reg_Label = Label(frame_reg, text="REGISTRATION", bg="#cac8c8", font=("Arial", 16))
    reg_Label.place(relx=0.5, rely=0.25, anchor=CENTER)

    reg_login_label = Label(frame_reg, text="Логін", bg="#cac8c8")
    reg_login_label.place(relx=0.5, rely=0.35, anchor=CENTER)

    reg_login_entry = Entry(frame_reg, bg="#d9d9d9", )
    reg_login_entry.place(relx=0.5, rely=0.44, anchor=CENTER)

    reg_pass_label = Label(frame_reg, text="Пароль", bg="#cac8c8")
    reg_pass_label.place(relx=0.5, rely=0.52, anchor=CENTER)

    reg_pass_entry = Entry(frame_reg, bg="#d9d9d9", show="*")
    reg_pass_entry.place(relx=0.5, rely=0.61, anchor=CENTER)

    reg_btn = Button(frame_reg, text="Зареєструватися", bg="#d9d9d9", command=lambda: on_registration(reg_login_entry.get(), reg_pass_entry.get()))
    reg_btn.place(relx=0.5, rely=0.75, anchor=CENTER)

    reg_msg_label = Label(frame_reg, text="", wraplength=200, bg="#cac8c8", fg="red")
    reg_msg_label.place(relx=0.5, rely=0.85, anchor=CENTER)

    #login frame
    return_btn = Button(frame_log, text="<-", bg="#d9d9d9", command=lambda: showFrame(frame_main))
    return_btn.place(relx=0.1, rely=0.1, anchor=CENTER)

    log_Label = Label(frame_log, text="LOGIN", bg="#cac8c8", font=("Arial", 16))
    log_Label.place(relx=0.5, rely=0.25, anchor=CENTER)
    
    log_login_label = Label(frame_log, text="Логін", bg="#cac8c8")
    log_login_label.place(relx=0.5, rely=0.35, anchor=CENTER)

    log_login_entry = Entry(frame_log, bg="#d9d9d9", )
    log_login_entry.place(relx=0.5, rely=0.44, anchor=CENTER)
    
    log_pass_label = Label(frame_log, text="Пароль", bg="#cac8c8")
    log_pass_label.place(relx=0.5, rely=0.52, anchor=CENTER)

    log_pass_entry = Entry(frame_log, bg="#d9d9d9", show="*")
    log_pass_entry.place(relx=0.5, rely=0.61, anchor=CENTER)

    log_btn = Button(frame_log, text="Увійти", bg="#d9d9d9", command=lambda: handle_login(log_login_entry.get(), log_pass_entry.get()))
    log_btn.place(relx=0.5, rely=0.75, anchor=CENTER)

    log_msg_label = Label(frame_log, text="", wraplength=200, bg="#cac8c8", fg="red")
    log_msg_label.place(relx=0.5, rely=0.85, anchor=CENTER)

root.mainloop()

if authenticated_session["user"]:
	if authenticated_session["is_admin"]:
		open_admin_window(authenticated_session["user"])
	else:
		open_profile_window(authenticated_session["user"])
