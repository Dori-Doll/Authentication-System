import tkinter as tk
from enter import (
	build_modal_birth_selection,
	build_admin_cards_data,
	build_user_profile_rows,
	get_family_status_options_display,
	get_locality_suggestions,
	get_modal_birth_day_options,
	get_modal_birth_month_options,
	get_modal_birth_year_options,
	get_sex_options_display,
	get_user_header_name,
	process_login_attempt,
	register_new_user,
	reset_lock_state,
)


def center_window(target_window, width, height):
	screen_width = target_window.winfo_screenwidth()
	screen_height = target_window.winfo_screenheight()
	x_coord = int((screen_width / 2) - (width / 2))
	y_coord = int((screen_height / 2) - (height / 2))
	target_window.geometry(f"{width}x{height}+{x_coord}+{y_coord}")


def select_dob_with_sequential_modals(parent_window):

	def open_choice_dialog(title, options, columns=4):
		selected_value = {"value": None}
		dialog = tk.Toplevel(parent_window)
		dialog.title(title)
		dialog.configure(bg="#f8fbff")
		dialog.resizable(False, False)
		dialog.transient(parent_window)
		dialog.grab_set()

		frame = tk.Frame(dialog, bg="#f8fbff")
		frame.pack(padx=16, pady=14)

		for idx, option in enumerate(options):
			button = tk.Button(
				frame,
				text=str(option),
				font=("Arial", 11),
				width=10,
				command=lambda value=option: (selected_value.__setitem__("value", value), dialog.destroy())
			)
			button.grid(row=idx // columns, column=idx % columns, padx=4, pady=4)

		cancel_button = tk.Button(
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

	years = get_modal_birth_year_options()
	selected_year = open_choice_dialog("Оберіть Рік", years, columns=5)
	if selected_year is None:
		return None
	selected_year = str(selected_year)

	months = get_modal_birth_month_options(selected_year)
	selected_month = open_choice_dialog("Оберіть Місяць", months, columns=4)
	if selected_month is None:
		return None
	selected_month = str(selected_month)

	days = get_modal_birth_day_options(selected_year, selected_month)
	selected_day = open_choice_dialog("Оберіть День", days, columns=6)
	if selected_day is None:
		return None

	return build_modal_birth_selection(selected_day, selected_month, selected_year)


def open_profile_window(user):
	profile_window = tk.Tk()
	profile_window.title(f"ОСОБИСТИЙ КАБІНЕТ: {user['username']}")
	profile_window.configure(bg="#eaf4ff")
	profile_window.resizable(False, False)
	center_window(profile_window, 700, 520)

	header_frame = tk.Frame(profile_window, bg="#1f5f8b", height=90)
	header_frame.pack(fill="x")

	header_title = tk.Label(
		header_frame,
		text=f"Вітаємо, {get_user_header_name(user)}",
		font=("Times New Roman", 24, "bold"),
		bg="#1f5f8b",
		fg="white"
	)
	header_title.pack(pady=(16, 0))

	header_subtitle = tk.Label(
		header_frame,
		text="Ваші персональні дані",
		font=("Arial", 12),
		bg="#1f5f8b",
		fg="#dbeeff"
	)
	header_subtitle.pack(pady=(4, 14))

	content_frame = tk.Frame(profile_window, bg="#f8fbff", bd=1, relief="solid")
	content_frame.pack(fill="both", expand=True, padx=20, pady=16)

	for row_index, (label_text, value_text) in enumerate(build_user_profile_rows(user)):
		field_label = tk.Label(
			content_frame,
			text=f"{label_text}:",
			font=("Arial", 12, "bold"),
			bg="#f8fbff",
			fg="#1f2a35",
			anchor="w"
		)
		field_label.grid(row=row_index, column=0, sticky="w", padx=(16, 10), pady=8)

		value_label = tk.Label(
			content_frame,
			text=value_text,
			font=("Arial", 12),
			bg="#f8fbff",
			fg="#2f3b48",
			anchor="w",
			justify="left",
			wraplength=430
		)
		value_label.grid(row=row_index, column=1, sticky="w", padx=(0, 16), pady=8)

	content_frame.grid_columnconfigure(1, weight=1)

	close_button = tk.Button(
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


def open_admin_window(admin_user):
	admin_window = tk.Tk()
	admin_window.title("ПАНЕЛЬ АДМІНА")
	admin_window.configure(bg="#f4f7fb")
	admin_window.resizable(False, False)
	center_window(admin_window, 980, 650)

	header_frame = tk.Frame(admin_window, bg="#103a5c", height=84)
	header_frame.pack(fill="x")

	header_title = tk.Label(
		header_frame,
		text=f"Панель Адміністратора: {admin_user.get('first_name', 'admin')}",
		font=("Times New Roman", 24, "bold"),
		bg="#103a5c",
		fg="white"
	)
	header_title.pack(pady=18)

	container = tk.Frame(admin_window, bg="#f4f7fb")
	container.pack(fill="both", expand=True, padx=18, pady=14)

	canvas = tk.Canvas(container, bg="#f4f7fb", highlightthickness=0)
	scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
	scrollable_frame = tk.Frame(canvas, bg="#f4f7fb")

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

	for card in build_admin_cards_data():
		user_card = tk.Frame(scrollable_frame, bg="#ffffff", bd=1, relief="solid")
		user_card.pack(fill="x", pady=8, padx=4)

		card_header = tk.Label(
			user_card,
			text=card["title"],
			font=("Arial", 13, "bold"),
			bg="#1f5f8b",
			fg="white",
			anchor="w",
			padx=12,
			pady=7
		)
		card_header.pack(fill="x")

		body_frame = tk.Frame(user_card, bg="#ffffff")
		body_frame.pack(fill="x", padx=12, pady=10)

		for row_index, (label_text, value_text) in enumerate(card["rows"]):
			field_label = tk.Label(
				body_frame,
				text=f"{label_text}:",
				font=("Arial", 11, "bold"),
				bg="#ffffff",
				fg="#1f2a35",
				anchor="w"
			)
			field_label.grid(row=row_index, column=0, sticky="w", pady=3, padx=(0, 8))

			value_label = tk.Label(
				body_frame,
				text=value_text,
				font=("Arial", 11),
				bg="#ffffff",
				fg="#2f3b48",
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

	close_button = tk.Button(
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


def lock_login_inputs():
	login_entry.config(state="disabled")
	password_entry.config(state="disabled")
	confirm_button.config(state="disabled")
	result_label.config(fg="#b22222")


def unlock_login_inputs():
	reset_lock_state()
	login_entry.config(state="normal")
	password_entry.config(state="normal")
	confirm_button.config(state="normal")
	password_entry.delete(0, tk.END)
	result_label.config(text="Можна спробувати ще раз.", fg="#1f5f8b")


def open_registration_window():
	registration_window = tk.Toplevel(window)
	registration_window.title("РЕЄСТРАЦІЯ")
	registration_window.configure(bg="#edf6ff")
	registration_window.resizable(False, False)
	center_window(registration_window, 760, 760)

	header = tk.Label(
		registration_window,
		text="Створення нового акаунта",
		font=("Times New Roman", 24, "bold"),
		bg="#edf6ff",
		fg="#123a5a"
	)
	header.pack(pady=(18, 10))

	form_frame = tk.Frame(registration_window, bg="#ffffff", bd=1, relief="solid")
	form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

	username_var = tk.StringVar()
	password_var = tk.StringVar()
	first_name_var = tk.StringVar()
	last_name_var = tk.StringVar()
	father_name_var = tk.StringVar()
	birth_place_var = tk.StringVar()
	birth_year_var = tk.StringVar(value="")
	birth_month_var = tk.StringVar(value="")
	birth_day_var = tk.StringVar(value="")
	birth_date_display_var = tk.StringVar(value="Не обрано")
	birth_date_selected = {"value": False}
	birth_place_selected = {"value": False}
	sex_options = get_sex_options_display()
	sex_var = tk.StringVar(value=sex_options[0] if sex_options else "")
	family_options = get_family_status_options_display(sex_var.get())
	family_status_var = tk.StringVar(value=family_options[0] if family_options else "")
	penalty_status_var = tk.StringVar()

	row = 0

	def add_labeled_entry(label_text, text_var, show=None):
		nonlocal row
		label = tk.Label(form_frame, text=label_text, font=("Arial", 12, "bold"), bg="#ffffff", anchor="w")
		label.grid(row=row, column=0, sticky="w", padx=(16, 10), pady=(10, 4))
		entry = tk.Entry(form_frame, textvariable=text_var, font=("Arial", 12), width=36, show=show)
		entry.grid(row=row, column=1, sticky="w", padx=(0, 16), pady=(10, 4))
		row += 1
		return entry

	add_labeled_entry("Логін", username_var)
	add_labeled_entry("Пароль", password_var, show="*")
	add_labeled_entry("Ім'я", first_name_var)
	add_labeled_entry("Прізвище", last_name_var)
	add_labeled_entry("По батькові", father_name_var)

	birth_date_label = tk.Label(form_frame, text="Дата народження", font=("Arial", 12, "bold"), bg="#ffffff", anchor="w")
	birth_date_label.grid(row=row, column=0, sticky="w", padx=(16, 10), pady=(10, 4))
	birth_date_frame = tk.Frame(form_frame, bg="#ffffff")
	birth_date_frame.grid(row=row, column=1, sticky="w", padx=(0, 16), pady=(10, 4))

	birth_date_value_label = tk.Label(
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

	birth_date_button = tk.Button(
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

	birth_place_label = tk.Label(form_frame, text="Місце народження", font=("Arial", 12, "bold"), bg="#ffffff", anchor="w")
	birth_place_label.grid(row=row, column=0, sticky="w", padx=(16, 10), pady=(10, 4))
	birth_place_entry = tk.Entry(form_frame, textvariable=birth_place_var, font=("Arial", 12), width=36)
	birth_place_entry.grid(row=row, column=1, sticky="w", padx=(0, 16), pady=(10, 4))
	row += 1

	suggestions_listbox = tk.Listbox(form_frame, font=("Arial", 11), height=6, width=45)
	suggestions_listbox.grid(row=row, column=1, sticky="w", padx=(0, 16), pady=(0, 6))
	suggestions_listbox.grid_remove()
	row += 1

	sex_label = tk.Label(form_frame, text="Стать", font=("Arial", 12, "bold"), bg="#ffffff", anchor="w")
	sex_label.grid(row=row, column=0, sticky="w", padx=(16, 10), pady=(10, 4))
	sex_menu = tk.OptionMenu(form_frame, sex_var, *sex_options)
	sex_menu.config(font=("Arial", 11), width=18)
	sex_menu.grid(row=row, column=1, sticky="w", padx=(0, 16), pady=(10, 4))
	row += 1

	family_label = tk.Label(form_frame, text="Сімейний стан", font=("Arial", 12, "bold"), bg="#ffffff", anchor="w")
	family_label.grid(row=row, column=0, sticky="w", padx=(16, 10), pady=(10, 4))
	family_menu = tk.OptionMenu(form_frame, family_status_var, *(family_options or [""]))
	family_menu.config(font=("Arial", 11), width=18)
	family_menu.grid(row=row, column=1, sticky="w", padx=(0, 16), pady=(10, 4))
	row += 1

	add_labeled_entry("Штрафи (необов'язково)", penalty_status_var)

	status_label = tk.Label(form_frame, text="", font=("Arial", 11, "bold"), bg="#ffffff", fg="#b22222")
	status_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=16, pady=(10, 4))
	row += 1

	def refresh_family_options(*_args):
		options = get_family_status_options_display(sex_var.get())
		menu = family_menu["menu"]
		menu.delete(0, "end")
		for option in options:
			menu.add_command(label=option, command=tk._setit(family_status_var, option))
		if options:
			family_status_var.set(options[0])
		else:
			family_status_var.set("")

	def update_locality_suggestions(*_args):
		birth_place_selected["value"] = False
		query = birth_place_var.get().strip()
		if len(query) < 2:
			suggestions_listbox.grid_remove()
			suggestions_listbox.delete(0, tk.END)
			return

		suggestions = get_locality_suggestions(query, limit=20)
		suggestions_listbox.delete(0, tk.END)
		for locality in suggestions:
			suggestions_listbox.insert(tk.END, locality)

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
			"username": username_var.get(),
			"password": password_var.get(),
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

		result = register_new_user(registration_data)
		if result["ok"]:
			status_label.config(text=result["message"], fg="#1f7a1f")
			registration_window.after(1200, registration_window.destroy)
		else:
			status_label.config(text=result["message"], fg="#b22222")

	birth_place_var.trace_add("write", update_locality_suggestions)
	sex_var.trace_add("write", refresh_family_options)
	suggestions_listbox.bind("<<ListboxSelect>>", select_suggestion)
	suggestions_listbox.bind("<Double-Button-1>", select_suggestion)
	birth_place_entry.bind("<Down>", lambda _e: suggestions_listbox.focus_set() if suggestions_listbox.size() else None)

	button_frame = tk.Frame(form_frame, bg="#ffffff")
	button_frame.grid(row=row, column=0, columnspan=2, pady=(12, 16))

	submit_button = tk.Button(
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

	cancel_button = tk.Button(
		button_frame,
		text="СКАСУВАТИ",
		font=("Arial", 12, "bold"),
		bg="#8a8f98",
		fg="white",
		activebackground="#9aa0aa",
		activeforeground="white",
		width=12,
		command=registration_window.destroy
	)
	cancel_button.pack(side="left", padx=8)

	form_frame.grid_columnconfigure(1, weight=1)


def handle_login():
	username = login_entry.get().strip()
	password = password_entry.get()
	login_result = process_login_attempt(username, password)

	if login_result["ok"]:
		authenticated_session["user"] = login_result["user"]
		authenticated_session["is_admin"] = login_result["is_admin"]
		window.destroy()
		return

	password_entry.delete(0, tk.END)
	result_label.config(text=login_result["message"], fg="#b22222")

	if login_result["locked"]:
		lock_login_inputs()
		window.after(login_result["retry_ms"], unlock_login_inputs)


authenticated_session = {"user": None, "is_admin": False}

window = tk.Tk()
window.title("ОСОБИСТИЙ КАБІНЕТ")

window_width = 550
window_height = 500

center_window(window, window_width, window_height)
window.resizable(False, False)

welcome_label = tk.Label(window, text="Ласкаво просимо\nдо\nОсобистого Кабінету", font=("Arial", 12, "bold"), justify="center")
welcome_label.config(font=("Times New Roman", 25, "bold"))
welcome_label.pack(pady=10)

hint_label = tk.Label(window, text="Будь ласка, введіть ваші дані", font=("Arial", 12))
hint_label.pack(pady=(5, 12))

login_label = tk.Label(window, text="Логін:", font=("Arial", 18))
login_label.pack(pady=(25, 5))

login_entry = tk.Entry(window, font=("Arial", 18), width=20)
login_entry.pack(pady=5)

password_label = tk.Label(window, text="Пароль:", font=("Arial", 18))
password_label.pack(pady=(35, 5))

password_entry = tk.Entry(window, font=("Arial", 18), width=20, show="*")
password_entry.pack(pady=5)

confirm_button = tk.Button(
	window,
	text="ПІДТВЕРДИТИ",
	font=("Arial", 14, "bold"),
	bg="#2e8b57",
	fg="white",
	activebackground="#3aa86b",
	activeforeground="white",
	width=16,
	command=handle_login
)
confirm_button.pack(pady=(18, 10))

register_button = tk.Button(
	window,
	text="РЕЄСТРАЦІЯ",
	font=("Arial", 12, "bold"),
	bg="#1f5f8b",
	fg="white",
	activebackground="#2b6f9f",
	activeforeground="white",
	width=16,
	command=open_registration_window
)
register_button.pack(pady=(0, 8))

result_label = tk.Label(window, text="", font=("Arial", 12, "bold"))
result_label.pack(pady=(4, 0))

window.mainloop()

if authenticated_session["user"]:
	if authenticated_session["is_admin"]:
		open_admin_window(authenticated_session["user"])
	else:
		open_profile_window(authenticated_session["user"])
