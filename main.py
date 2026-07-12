import json
import os
#import UrlRequests

import urllib.parse
#import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup

from datetime import datetime, timedelta
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from jnius import autoclass


SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzgzsgZCbdYex2DQfKpGCEic6xwgdf10t7K3TAW9hA8o8qOirqA4k6SPLggP423BuI/exec"
app_data = {"companies": {}, "prices": {}}

def save_data(data):
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving data: {e}")

def load_data(app_instance=None):
    global app_data
    # 1. تحميل الملف الموجود محلياً فوراً
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            try:
                app_data.update(json.load(f))
            except: pass
    
    # 2. تحديث البيانات من الإنترنت في الخلفية
    def update_from_net(req, result):
        if result:
            app_data.update(result)
            save_data(app_data)
            if app_instance: app_instance.refresh_ui()

    # طلب البيانات من جوجل شيت
    UrlRequest(SCRIPT_URL, on_success=update_from_net)
    
    # تحديث الواجهة
    if app_instance:
        app_instance.refresh_ui()

def fix_and_reshape_arabic(text):
    if not text:
        return ""
    
    # 1. إذا كان النص يحتوي على أرقام فقط أو رموز، نتركه كما هو دون تعديل
    # هذا يحل مشكلة ظهور المربعات في أرقام الهواتف والتواريخ
    if not any(0x0600 <= ord(c) <= 0x06FF for c in text):
        return text 

    # 2. قاموس الحروف العربية (كما هو في الكود الأصلي)
    arabic_glyphs = {
        'ا': ('ا', 'ﺎ', 'ﺎ', 'ا'), 'ب': ('ب', 'ﺑ', 'ﺒ', 'ﺐ'), 'ت': ('ت', 'ﺗ', 'ﺘ', 'ﺖ'),
        'ث': ('ث', 'ﺛ', 'ﺜ', 'ﺚ'), 'ج': ('ج', 'ﺟ', 'ﺠ', 'ﺞ'), 'ح': ('ح', 'ﺣ', 'ﺤ', 'ﺢ'),
        'خ': ('خ', 'ﺧ', 'ﺨ', 'ﺦ'), 'د': ('د', 'ﺪ', 'ﺪ', 'د'), 'ذ': ('ذ', 'ﺬ', 'ﺬ', 'ذ'),
        'ر': ('ر', 'ﺮ', 'ﺮ', 'ر'), 'ز': ('ز', 'ﺰ', 'ﺰ', 'ز'), 'س': ('س', 'ﺳ', 'ﺴ', 'ﺲ'),
        'ش': ('ش', 'ﺷ', 'ﺸ', 'ﺶ'), 'ص': ('ص', 'ﺻ', 'ﺼ', 'ﺺ'), 'ض': ('ض', 'ﺿ', 'ﻀ', 'ﺾ'),
        'ط': ('ط', 'ﻃ', 'ﻄ', 'ﻂ'), 'ظ': ('ظ', 'ﻇ', 'ﻈ', 'ﻆ'), 'ع': ('ع', 'ﻋ', 'ﻌ', 'ﻊ'),
        'غ': ('غ', 'ﻏ', 'ﻐ', 'ﻎ'), 'ف': ('ف', 'ﻓ', 'ﻔ', 'ﻒ'), 'ق': ('ق', 'ﻗ', 'ﻘ', 'ﻖ'),
        'ك': ('ك', 'ﻛ', 'ﻜ', 'ﻚ'), 'ل': ('ل', 'ﻟ', 'ﻠ', 'ﻞ'), 'م': ('م', 'ﻣ', 'ﻤ', 'ﻢ'),
        'ن': ('ن', 'ﻧ', 'ﻨ', 'ﻦ'), 'ه': ('ه', 'ﻫ', 'ﻬ', 'ﻪ'), 'و': ('و', 'ﻮ', 'ﻮ', 'و'),
        'ي': ('ي', 'ﻳ', 'ﻴ', 'ﻲ'), 'ة': ('ة', 'ﺔ', 'ﺔ', 'ة'), 'ى': ('ى', 'ﻰ', 'ﻰ', 'ى'),
        'أ': ('أ', 'ﺄ', 'ﺄ', 'أ'), 'إ': ('إ', 'ﺈ', 'ﺈ', 'إ'), 'لأ': ('لأ', 'ﻼ', 'ﻼ', 'لأ'),
        'لا': ('لا', 'ﻼ', 'ﻼ', 'لا'), 'آ': ('آ', 'ﺂ', 'ﺂ', 'آ')
    }
    
    non_connectors = ['ا', 'د', 'ذ', 'ر', 'ز', 'و', 'ة', 'أ', 'إ', 'ى', 'آ']
    words = text.split(" ")
    reshaped_words = []
    
    for word in words:
        if not word:
            continue
            
        # إذا كانت الكلمة أرقاماً، أضفها كما هي
        if not any(0x0600 <= ord(c) <= 0x06FF for c in word):
            reshaped_words.append(word)
            continue
            
        reshaped_word = ""
        n = len(word)
        for i in range(n):
            char = word[i]
            if char in arabic_glyphs:
                is_connected_before = i > 0 and word[i-1] in arabic_glyphs and word[i-1] not in non_connectors
                is_connected_after = i < n-1 and word[i+1] in arabic_glyphs
                
                if is_connected_before and is_connected_after: reshaped_word += arabic_glyphs[char][2]
                elif is_connected_before: reshaped_word += arabic_glyphs[char][3]
                elif is_connected_after: reshaped_word += arabic_glyphs[char][1]
                else: reshaped_word += arabic_glyphs[char][0]
            else:
                reshaped_word += char
        
        # قلب الكلمة لضبط الاتجاه في Kivy
        reshaped_words.append(reshaped_word[::-1])
        
    return " ".join(reshaped_words[::-1])


# استدعاء آمن من ملف قاعدة البيانات المعدل
try:
    from database import add_booking_to_sheets, sync_local_data_to_sheets, init_local_db
except Exception:
    def init_local_db(): pass
    def sync_local_data_to_sheets(): pass
    def add_booking_to_sheets(data, total, msg): return "local_success"
def revert_reshaped_arabic(text):
    # هذه الدالة تعيد النص المقلوب إلى حالته الأصلية
    # الكود الذي استخدمته يعتمد على [::-1] في التشكيل، لذا العكس هنا بسيط
    if not text:
        return ""
    # نقوم بعكس النص ليعود إلى ترتيبه الصحيح قبل الإرسال
    return text[::-1]

class OrderFormScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_date = "" 
        self.name = "form"
        self.inputs = {}
        # أضف هذا المتغير في __init__
        self.selected_date = "2026-07-06" # التاريخ الافتراضي


        with self.canvas.before:
            Color(0.12, 0.12, 0.24, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            # داخل __init__
            

    
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        main_layout = BoxLayout(orientation='vertical', padding=35, spacing=20)
        
        top_bar = BoxLayout(size_hint_y=0.1)
        with top_bar.canvas.before:
            Color(0.08, 0.08, 0.18, 1)
        # داخل OrderFormScreen في الـ top_bar:
        top_bar = BoxLayout(size_hint_y=0.1, orientation='horizontal')
        
        title_lbl = Label(text=fix_and_reshape_arabic("   44764140010\nلاشتراك الشركات اتصل علي \nتطبيق أولاد مصر"), font_size=30, font_name="AndroidArabic")
        
        btn_login = Button(text=fix_and_reshape_arabic("دخول"), size_hint_x=0.5, font_name="AndroidArabic")
        btn_login.bind(on_release=lambda x: setattr(self.manager, 'current', 'login'))
        
        top_bar.add_widget(title_lbl)
        top_bar.add_widget(btn_login)
        main_layout.add_widget(top_bar)

        
        scroll = ScrollView(size_hint_y=0.8, bar_width=10, scroll_type=['bars', 'content'])
        grid = GridLayout(cols=1, spacing=12, size_hint_y=None, padding=[5, 10, 5, 10])
        grid.bind(minimum_height=grid.setter('height'))
        
        # قائمة الحقول
        fields = [
            ('type', "", "spinner"), ('name', "اسم العميل:", "text"),
            ('phone', "رقم الهاتف:", "text_int"),
            ('wrapping_rooms', "عدد غرف التغليف:", "text_int"),
            ('dismantling_rooms', "عدد غرف الفك والتركيب:", "text_int"),
            ('air_conditioners', "عدد التكييفات:", "text_int"),
            ('floor_up', "الطابق (صعود):", "text_int"),
            ('floor_down', "الطابق (نزول):", "text_int"),
            ('bedrooms', "عدد غرف النوم:", "text_int"),
            ('living_rooms', "عدد غرف الانتريه والليفنج:", "text_int"),
            ('kitchen_pieces', "عدد قطع المطبخ:", "text_int"),
            ('kids_rooms', "عدد غرف الاطفال:", "text_int"),
            ('dining_rooms', "عدد غرف السفره:", "text_int"),
            ('appliances', "عدد الاجهزة:", "text_int"),
            ('chandeliers', "عدد النجف:", "text_int"),
            ('cartons', "عدد الكراتين للتعبئة:", "text_int"),
            ('truck_type', "نوع سيارة النقل:", "spinner_truck"),
            ('winch_up', "نوع ونش الصعود:", "spinner_winch"),
            ('winch_down', "نوع ونش النزول:", "spinner_winch"),
            ('from_gov', "من منطقة (القاهرة الكبري):", "spinner_gov"),
            ('to_gov', "إلى منطقة (القاهرة الكبري):", "spinner_gov"),
            ('company', "اختر شركة النقل:", "spinner_company")
        ]
        
        gov_options = ["السادس من اكتوبر", "العجوزة","المطرية","شبرا مصر","حلوان","حدائق حلوان","حدائق الاهرام","الهرم","فيصل","السلام","عين شمس","القاهرة الجديدة","المقطم","مصر الجديدة","مصر القديمة","مدينتي","مدينة بدر","المهندسين","المطرية","العباسية", "العاصمة الإدارية", "الرحاب","مدينة نصر", "التجمع الاول", "الشروق","المرج","العبور","التجمع الخامس" ,"شبرا مصر"]
        winch_options = ["بدون ونش عن طريق السلم", "ونش هيدروليك خارجي", "ونش كهربائي مخصص"]
        truck_options = ["سيارة نقل مغلقة كبيرة 6متر ", "سيارة نقل مغلقة متوسطة4متر", "سيارة نقل متوسطة مفتوحة"]
        
        # إضافة الحقول لـ grid
        # داخل حلقة الـ for في __init__:
        for key, label_text, field_type in fields:
            lbl = Label(text=fix_and_reshape_arabic(label_text), font_size=35, font_name="AndroidArabic", size_hint_y=None, height=40, halign='right', color=(1, 0.84, 0, 1))
            grid.add_widget(lbl)
            
            if field_type in ["text", "text_int"]:
                inp = TextInput(multiline=False, font_name="AndroidArabic", size_hint_y=None, height=45, background_color=(0.08, 0.08, 0.18, 1), foreground_color=(1, 1, 1, 1))
                if field_type == "text_int": inp.input_filter = 'int'
                grid.add_widget(inp)
                self.inputs[key] = inp
            else: 
                # هذا الجزء كان خارج حلقة الـ for أو به خطأ في المسافات
                if "gov" in field_type: opts = gov_options
                elif "winch" in field_type: opts = winch_options
                elif "company" in field_type: opts = list(app_data.get("companies", {}).keys()) or ["....."]
                else: opts = truck_options
                
                sp = Spinner(text=fix_and_reshape_arabic(opts[0] if opts else "خطأ"), values=[fix_and_reshape_arabic(o) for o in opts], size_hint_y=None, height=45, font_name="AndroidArabic")
                sp.option_cls.font_name = "AndroidArabic"
                grid.add_widget(sp)
                self.inputs[key] = sp
                if "company" in field_type:
                    self.company_spinner = sp

        btn_date = Button(text=fix_and_reshape_arabic("اختر تاريخ النقل"), size_hint_y=None, height=50, background_color=(0, 0.5, 0.8, 1), font_name="AndroidArabic")
        btn_date.bind(on_release=self.open_date_picker)
        grid.add_widget(btn_date)
        
        scroll.add_widget(grid)
        main_layout.add_widget(scroll)
        
        # الأزرار السفلية


        # الأزرار السفلية - ابحث عن هذا الجزء:
        btn_settings = Button(
            text=fix_and_reshape_arabic("إعدادات الشركات"), 
            size_hint_y=0.08, 
            font_name="AndroidArabic", 
            background_color=(0.2, 0.2, 0.4, 1)
        )
        
        # استبدل السطر القديم بهذا السطر الجديد:
        btn_settings.bind(on_release=lambda x: setattr(self.manager, 'current', 'login'))
        
        #main_layout.add_widget(btn_settings)

        # ... (باقي الكود) ...

        btn_submit = Button(text=fix_and_reshape_arabic("عرض الفاتورة وإرسال البيانات"), size_hint_y=0.1, font_name="AndroidArabic", font_size=35, background_color=(1, 0.84, 0, 1), color=(0.12, 0, 0.24, 1), bold=True)
        btn_submit.bind(on_release=self.submit_data)
        main_layout.add_widget(btn_submit)
        
        self.add_widget(main_layout)

    def get_active_companies(self):
        active_companies = []
        companies = app_data.get("companies", {})
        for name, info in companies.items():
            status = info.get("active", True)
            if status is True or str(status).lower() == 'true':
                active_companies.append(name)
        return active_companies


    def on_kv_post(self, base_widget):
        if hasattr(self, 'company_spinner'):
            self.company_spinner.values = self.get_active_companies()



    def update_company_spinner(self, *args):
        # التأكد من أن transport_companies معرفة أو استخدام app_data
        companies = list(app_data.get("companies", {}).keys())
        if companies:
            self.company_spinner.values = [fix_and_reshape_arabic(o) for o in companies]
            self.company_spinner.text = fix_and_reshape_arabic(companies[0])

    def open_date_picker(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        date_layout = BoxLayout(size_hint_y=None, height=50, spacing=5)
        
        year_sp = Spinner(text="2026", values=["2026", "2027", "2028"])
        month_sp = Spinner(text="07", values=[f"{i:02d}" for i in range(1, 13)])
        day_sp = Spinner(text="04", values=[f"{i:02d}" for i in range(1, 32)])
        
        date_layout.add_widget(year_sp)
        date_layout.add_widget(month_sp)
        date_layout.add_widget(day_sp)
        content.add_widget(date_layout)
        
        btn_save = Button(text=fix_and_reshape_arabic("حفظ التاريخ"),font_name="AndroidArabic", size_hint_y=None, height=50)
        
        def save_date_action(btn):
            self.selected_date = f"{year_sp.text}-{month_sp.text}-{day_sp.text}"
            self.popup.dismiss()
            
        btn_save.bind(on_release=save_date_action)
        content.add_widget(btn_save)
        self.popup = Popup(title=fix_and_reshape_arabic("اختر التاريخ"), content=content, size_hint=(0.9, 0.5))
        self.popup.open()

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    def _update_sub_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
        
    def submit_data(self, instance):
        data = {}
        for key, widget in self.inputs.items():
            if hasattr(widget, 'text'):
                data[key] = widget.text.strip()
            else:
                data[key] = ""
        
        # 1. تجهيز البيانات الأساسية
        selected_comp_name = data.get('company')
        phone_found = "غير محدد"
        data['move_date'] = self.selected_date
        
        # التعديل هنا: نقارن النص المشكل بالاسم الأصلي للشركة
        for name, info in app_data["companies"].items():
            if fix_and_reshape_arabic(name) == selected_comp_name: 
                phone_found = info.get("phone", "غير محدد")
                break
        
        # 2. الحساب
        result = self.calculate_furniture_cost(data)
        
        # 3. بناء نص الفاتورة (استخدام دمج النصوص المباشر)
        invoice_text = (
            fix_and_reshape_arabic("--- فاتورة حجز نقل الأثاث ---") + "\n\n" +
            fix_and_reshape_arabic("الاسم") + " : " + data.get('name', '') + "\n" +
            fix_and_reshape_arabic("الهاتف") + " : " + data.get('phone', '') + "\n" +
            fix_and_reshape_arabic("الشركة المختارة") + " : " + data.get('company', '') + "\n" +
            fix_and_reshape_arabic("هاتف الشركة") + " : " + str(phone_found) + "\n" +
            fix_and_reshape_arabic("من") + " : " + data.get('from_gov', '') + "\n" +
            fix_and_reshape_arabic("إلى") + " : " + data.get('to_gov', '') + "\n" +
            fix_and_reshape_arabic("من الدور") + " : " + data.get('floor_down', '') + "\n" +
            fix_and_reshape_arabic("إلى الدور") + " : " + data.get('floor_up', '') + "\n" +
            fix_and_reshape_arabic("من الدور بالونش او بدون") + " : " + data.get('winch_up', '') + "\n" +
            fix_and_reshape_arabic("إلى الدور بالونش او بدون") + " : " + data.get('winch_down', '') + "\n" +
           
            fix_and_reshape_arabic("موعد النقل") + " : " + str(data.get('move_date', '')) + "\n\n" +
            
            f"{fix_and_reshape_arabic('غرف التغليف')} : {data.get('wrapping_rooms')}\n"
            f"{fix_and_reshape_arabic('غرف الفك والتركيب')} : {data.get('dismantling_rooms')}\n"
            f"{fix_and_reshape_arabic('التكييفات')} : {data.get('air_conditioners')}\n"
            f"{fix_and_reshape_arabic('غرف النوم')} : {data.get('bedrooms')}\n"
            f"{fix_and_reshape_arabic('غرف المعيشة')} : {data.get('living_rooms')}\n"
            f"{fix_and_reshape_arabic('قطع المطبخ')} : {data.get('kitchen_pieces')}\n"
            f"{fix_and_reshape_arabic('غرف الأطفال')} : {data.get('kids_rooms')}\n"
            f"{fix_and_reshape_arabic('غرف السفرة')} : {data.get('dining_rooms')}\n"
            f"{fix_and_reshape_arabic('الأجهزة')} : {data.get('appliances')}\n"
            f"{fix_and_reshape_arabic('النجف')} : {data.get('chandeliers')}\n"
            f"{fix_and_reshape_arabic('الكراتين')} : {data.get('cartons')}\n"
            f"{fix_and_reshape_arabic('نوع السيارة')} : {data.get('truck_type')}\n\n"
            f"{fix_and_reshape_arabic('الإجمالي بالجنيه')} : {result['total']}\n"
            f"{fix_and_reshape_arabic(' سيتم توجيهك الي الوتس الخاص بالشركة')}"
            
        )            
        
        
        invoice_screen = self.manager.get_screen('invoice')
        invoice_screen.lbl_content.text = invoice_text
        self.manager.current = 'invoice'
     
    def calculate_furniture_cost(self, data):
        try:
            import re
            # الأسعار الافتراضية في حال لم تكن البيانات قد وصلت بعد
            default_prices = {
                "room_cost": 1000, "ac_kitchen_cost": 150, 
                "dismantle_cost": 100, "winch_cost": 500, 
                "truck_cost": 800, "min_total": 4000
            }
            
            # جلب الأسعار من app_data أو استخدام الافتراضية
            prices = app_data.get("prices", default_prices)
            if not prices: prices = default_prices

            def get_val(key):
                val = str(data.get(key, "0"))
                numbers = re.findall(r'\d+', val)
                return int(numbers[0]) if numbers else 0

            # الحساب بناءً على المفاتيح الموجودة
            rooms_total = (get_val('bedrooms') + get_val('living_rooms') + 
                           get_val('kids_rooms') + get_val('dining_rooms') + 
                           get_val('wrapping_rooms'))
            
            total = (rooms_total * prices.get("room_cost", 1000)) + \
                    ((get_val('air_conditioners') + get_val('kitchen_pieces')) * prices.get("ac_kitchen_cost", 150)) + \
                    (get_val('dismantling_rooms') * prices.get("dismantle_cost", 200))
            
            total += prices.get("winch_cost", 500) if "بدون ونش" not in data.get('winch_up', "") else 0
            
            truck_type = data.get('truck_type', "")
            if "كبيرة" in truck_type:
                total += prices.get("truck_cost", 800)
            elif "متوسطة" in truck_type:
                total += (prices.get("truck_cost", 800) * 0.8)     
            
            if total < prices.get("min_total", 4000): 
                total = prices.get("min_total", 4000)
            
            # تطبيق معامل الشركة
            selected_company_text = data.get('company', "")
            factor = 1.0
            companies = app_data.get("companies", {})
            for original_name, info in companies.items():
                if fix_and_reshape_arabic(original_name) == selected_company_text:
                    factor = info.get("factor", 1.0)
                    break
            
            final_total = int(total * factor)
            return {"status": "success", "total": final_total}
            
        except Exception as e:
            print(f"Error calculating cost: {e}")
            return {"status": "error", "total": 0}


class InvoiceScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "invoice"
        with self.canvas.before:
            Color(0.12, 0.12, 0.24, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        title = Label(text=fix_and_reshape_arabic("فاتورة حجز نقل الأثاث"), font_size=50, font_name="AndroidArabic", bold=True, size_hint_y=0.1, color=(1, 0.84, 0, 1))
        layout.add_widget(title)
        
        scroll = ScrollView(size_hint_y=0.8)
        self.lbl_content = Label(text="", font_size=30, font_name="AndroidArabic", color=(1, 1, 1, 1), halign='center', valign='middle', size_hint_y=None)
        self.lbl_content.bind(texture_size=self.lbl_content.setter('size'))
        self.bind(width=lambda inv, w: setattr(inv.lbl_content, 'text_size', (w - 40, None)))
        scroll.add_widget(self.lbl_content)
        layout.add_widget(scroll)
        
        btn_back = Button(text=fix_and_reshape_arabic("رجوع وتعديل البيانات"), font_name="AndroidArabic", size_hint_y=0.1, font_size=25, background_normal='', background_color=(0.08, 0.08, 0.18, 1), color=(1, 0.84, 0, 1), bold=True)
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'form'))
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def on_pre_enter(self):
        Clock.schedule_once(self.auto_process_data, 5)
    def auto_process_data(self, dt):
        form_screen = self.manager.get_screen('form')
        
        # 1. جمع البيانات
        data = {}
        for key, widget in form_screen.inputs.items():
            data[key] = widget.text if hasattr(widget, 'text') else "0"
        
        calc_result = form_screen.calculate_furniture_cost(data)
        data['total'] = str(calc_result.get('total', 4100))
        data['move_date'] = str(form_screen.selected_date)
        
        # 2. تجهيز البيانات للإرسال (عكس النصوص العربية)
        def clean_text(text):
            if not text: return ""
            if text.isdigit() or '-' in text: return text
            return text[::-1] # عكس النص ليعود صحيحاً في الشيت

        sheet_data = {k: clean_text(str(v)) for k, v in data.items()}
        
        # 3. إرسال البيانات (تأكد أن الرابط هو نفس الرابط المستخدم في Apps Script)
        url = "https://script.google.com/macros/s/AKfycbzgzsgZCbdYex2DQfKpGCEic6xwgdf10t7K3TAW9hA8o8qOirqA4k6SPLggP423BuI/exec"
        
        UrlRequest(
            url, 
            req_body=json.dumps(sheet_data), 
            method='POST', 
            req_headers={'Content-Type': 'application/json'},
            on_success=lambda req, res: print("تم إرسال الفاتورة بنجاح: " + res),
            on_error=lambda req, err: print(f"خطأ في إرسال الفاتورة: {err}")
        )
        
        # 4. إرسال الواتساب
        self.trigger_sms(data)

    def trigger_sms(self, data):
        # 1. دالة مساعدة لعكس التشكيل عند الحاجة
        def prepare_text(text):
            # إذا كان النص مقلوباً (يحتوي على حروف عربية)، نعكسه
            # ملاحظة: نستخدم revert_reshaped_arabic التي عرفتها سابقاً
            return revert_reshaped_arabic(text)

        # 2. تحديد هاتف الشركة
        phone = "+201004146744" 
        for name, info in app_data["companies"].items():
            # نقارن باستخدام الاسم المعكوس (لأن data.get('company') مخزنة بشكل مقلوب)
            if fix_and_reshape_arabic(name) == data.get('company'):
                phone = info.get("phone", "201004146744").replace("+", "").replace(" ", "")
                break
    
        # 3. بناء نص الرسالة مع عكس القيم المقلوبة
        # نستخدم prepare_text لكل القيم التي قد تكون مقلوبة
        msg_lines = [
            "طلب نقل أثاث جديد:",
            f"العميل: {data.get('name', 'غير محدد')}",
            f"الهاتف: {data.get('phone', 'غير محدد')}",
            f"تاريخ النقل: {data.get('move_date', 'غير محدد')}",
            "--- تفاصيل الحجز ---",
            f"غرف التغليف: {data.get('wrapping_rooms', '0')}",
            f"غرف الفك والتركيب: {data.get('dismantling_rooms', '0')}",
            f"التكييفات: {data.get('air_conditioners', '0')}",
            f"غرف النوم: {data.get('bedrooms', '0')}",
            f"غرف الليفنج: {data.get('living_rooms', '0')}",
            f"قطع المطبخ: {data.get('kitchen_pieces', '0')}",
            f"غرف الأطفال: {data.get('kids_rooms', '0')}",
            f"غرف السفرة: {data.get('dining_rooms', '0')}",
            f"الأجهزة: {data.get('appliances', '0')}",
            f"النجف: {data.get('chandeliers', '0')}",
            f"الكراتين: {data.get('cartons', '0')}",
            f"نوع السيارة: {prepare_text(data.get('truck_type', 'غير محدد'))}",
            f"طريقة الصعود: {prepare_text(data.get('winch_up', 'غير محدد'))}",
            f"طريقة النزول: {prepare_text(data.get('winch_down', 'غير محدد'))}",
            f"النقل من: {prepare_text(data.get('from_gov', 'غير محدد'))}",
            f"النقل إلى: {prepare_text(data.get('to_gov', 'غير محدد'))}",
            f"الطابق صعود: {data.get('floor_up', 'غير محدد')}",
            f"الطابق نزول: {data.get('floor_down', 'غير محدد')}",
            "----------------",
            f"الإجمالي: {data.get('total', '4030')} ج.م"
        ]
        
        full_msg = "\n".join(msg_lines)
    
        # 4. باقي الكود الخاص بفتح الواتساب (بدون تغيير)
        encoded_msg = urllib.parse.quote(full_msg)
        url = f"https://wa.me/{phone}?text={encoded_msg}"
        
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
    
        intent = Intent(Intent.ACTION_VIEW)
        intent.setData(Uri.parse(url))
        intent.setPackage("com.whatsapp")
    
        try:
            PythonActivity.mActivity.startActivity(intent)
        except:
            intent.setPackage(None)
            PythonActivity.mActivity.startActivity(intent)


    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        print(f"Current app_data keys: {list(app_data.keys())}")

        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        # الحقول
        self.name_inp = TextInput(hint_text=fix_and_reshape_arabic("اسم شركة جديدة"), font_name="AndroidArabic", multiline=False, size_hint_y=None, height=45)
        self.factor_inp = TextInput(hint_text=fix_and_reshape_arabic("معامل الشركة"), font_name="AndroidArabic", multiline=False, size_hint_y=None, height=45)
        self.room_price = TextInput(text=str(app_data.get("prices", {}).get("room_cost", 1000)), font_name="AndroidArabic", size_hint_y=None, height=45, multiline=False)
        self.ac_price = TextInput(text=str(app_data.get("prices", {}).get("ac_kitchen_cost", 150)), font_name="AndroidArabic", size_hint_y=None, height=45, multiline=False)
        self.dismantle_price = TextInput(text=str(app_data.get("prices", {}).get("dismantle_cost", 100)), font_name="AndroidArabic", size_hint_y=None, height=45, multiline=False)
        self.winch_price = TextInput(text=str(app_data.get("prices", {}).get("winch_cost", 500)), font_name="AndroidArabic", size_hint_y=None, height=45)
        self.truck_price = TextInput(text=str(app_data.get("prices", {}).get("truck_cost", 800)), font_name="AndroidArabic", size_hint_y=None, height=45)
        self.min_price = TextInput(text=str(app_data.get("prices", {}).get("min_total", 4000)), font_name="AndroidArabic", size_hint_y=None, height=45, multiline=False)
        self.phone_inp = TextInput(hint_text="01xxxxxxxxx", input_filter='int', multiline=False, size_hint_y=None, height=45)
        
        self.old_pass = TextInput(hint_text=fix_and_reshape_arabic("كلمة المرور القديمة"), font_name="AndroidArabic", password=True, multiline=False, size_hint_y=None, height=45)
        self.new_pass = TextInput(hint_text=fix_and_reshape_arabic("كلمة المرور الجديدة"), font_name="AndroidArabic", password=True, multiline=False, size_hint_y=None, height=45)

        # إضافة العناصر
        def add_item(widget, label_text=None):
            if label_text: self.grid.add_widget(Label(text=fix_and_reshape_arabic(label_text), font_name="AndroidArabic", size_hint_y=None, height=30, color=(1, 0.84, 0, 1)))
            self.grid.add_widget(widget)

        add_item(self.name_inp, "إضافة شركة جديدة:")
        add_item(self.factor_inp, "معامل الشركة:")
        add_item(self.room_price, "سعر الغرفة:")
        add_item(self.ac_price, "سعر التكييف/المطبخ:")
        add_item(self.dismantle_price, "سعر الفك والتركيب:")
        add_item(self.min_price, "الحد الأدنى للفاتورة:")
        add_item(self.winch_price, "سعر الونش:")
        add_item(self.truck_price, "سعر السيارة:")
        add_item(self.phone_inp, "هاتف الشركة:")
        
        self.grid.add_widget(Label(text=fix_and_reshape_arabic("قائمة الشركات:"), size_hint_y=None, font_name="AndroidArabic", height=40))
        self.companies_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.companies_layout.bind(minimum_height=self.companies_layout.setter('height'))
        self.grid.add_widget(self.companies_layout)
        
        add_item(self.old_pass, "تغيير كلمة المرور:")
        self.grid.add_widget(self.new_pass)
        btn_pass = Button(text=fix_and_reshape_arabic("حفظ كلمة المرور الجديدة"), font_name="AndroidArabic", size_hint_y=None, height=50, background_color=(0.8, 0.2, 0.2, 1), on_release=self.change_password)
        self.grid.add_widget(btn_pass)

        btn_save = Button(text=fix_and_reshape_arabic("حفظ كل الإعدادات"), font_name="AndroidArabic", size_hint_y=None, height=50, background_color=(0, 0.6, 0, 1), on_release=self.save_all)
        btn_back = Button(text=fix_and_reshape_arabic("رجوع"), font_name="AndroidArabic", size_hint_y=None, height=50, on_release=lambda x: setattr(self.manager, 'current', 'form'))
        
        self.grid.add_widget(btn_save)
        self.grid.add_widget(btn_back)
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)
        self.add_widget(layout)
        self.build_company_list()

    def save_all(self, instance):
        # تحديث الأسعار
        app_data["prices"] = {
            "room_cost": int(self.room_price.text),
            "ac_kitchen_cost": int(self.ac_price.text),
            "dismantle_cost": int(self.dismantle_price.text),
            "winch_cost": int(self.winch_price.text),
            "truck_cost": int(self.truck_price.text),
            "min_total": int(self.min_price.text)
        }
        # إضافة شركة جديدة إذا وجد اسم
        if self.name_inp.text:
            app_data["companies"][self.name_inp.text] = {
                "factor": float(self.factor_inp.text) if self.factor_inp.text else 1.0,
                "phone": self.phone_inp.text,
                "active": True
            }
        save_data(app_data)
        self.build_company_list()
        print("تم حفظ الإعدادات بنجاح!")

    def build_company_list(self):
        self.companies_layout.clear_widgets()
        for name, info in app_data.get("companies", {}).items():
            row = BoxLayout(size_hint_y=None, height=40, spacing=5)
            row.add_widget(Label(text=fix_and_reshape_arabic(name),font_name="AndroidArabic", size_hint_x=0.4))
            btn_status = Button(text=fix_and_reshape_arabic("تعليق" if info.get("active", True) else "تفعيل"),font_name="AndroidArabic", size_hint_x=0.3)
            btn_status.bind(on_release=lambda x, n=name: self.toggle_company(n))
            btn_del = Button(text=fix_and_reshape_arabic("حذف"),font_name="AndroidArabic" , size_hint_x=0.3, background_color=(1, 0, 0, 1))
            btn_del.bind(on_release=lambda x, n=name: self.delete_company(n))
            row.add_widget(btn_status)
            row.add_widget(btn_del)
            self.companies_layout.add_widget(row)

    def change_password(self, instance):
        # نقوم بتحديث كلمة المرور في app_data يدوياً
        if "W@el241999" not in app_data:
            app_data["W@el241999"] = {}
        
        # تحويل الجديدة إلى Hash ليطابق منطق الدخول
        import hashlib
        new_pass_hash = hashlib.sha256(self.new_pass.text.encode('utf-8')).hexdigest()
        
        # تحديث القاموس وحفظ الملف
        app_data["W@el241999"]["pass"] = new_pass_hash
        app_data["W@el241999"]["user"] = "W@el241999"
        save_data(app_data)
        
        self.old_pass.text = ""
        self.new_pass.text = ""
        print("تم حفظ كلمة المرور الجديدة بنجاح")

    def toggle_company(self, name):
        app_data["companies"][name]["active"] = not app_data["companies"][name].get("active", True)
        save_data(app_data)
        self.build_company_list()

    def delete_company(self, name):
        if name in app_data["companies"]:
            del app_data["companies"][name]
            save_data(app_data)
            self.build_company_list()


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        self.user_inp = TextInput(hint_text=fix_and_reshape_arabic("اسم المستخدم"), font_name="AndroidArabic", multiline=False)
        self.pass_inp = TextInput(hint_text=fix_and_reshape_arabic("كلمة السر"), font_name="AndroidArabic", multiline=False, password=True)
        btn = Button(text=fix_and_reshape_arabic("دخول للإعدادات"), font_name="AndroidArabic", on_release=self.check_login)
        
        layout.add_widget(Label(text=fix_and_reshape_arabic("تسجيل الدخول"), font_name="AndroidArabic"))
        layout.add_widget(self.user_inp)
        layout.add_widget(self.pass_inp)
        layout.add_widget(btn)
        self.add_widget(layout)

    def check_login(self, instance):
        # بدلاً من البحث عن المفتاح W@el241999 الذي يسبب المشكلة
        # سنضع بيانات الدخول مباشرة للمقارنة أو نبحث عنها بطريقة مختلفة
        
        # كلمة السر التي وضعتها في الملف هي المشفرة بهذا الـ Hash
        saved_pass = "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"
        
        # تشفير المدخل للمقارنة
        import hashlib
        entered_password = self.pass_inp.text.encode('utf-8')
        hashed_input = hashlib.sha256(entered_password).hexdigest()
        
        # المقارنة:
        if self.user_inp.text == "W@el241999" and hashed_input == saved_pass:
            self.manager.current = 'settings'
        else:
            self.user_inp.text = ""
            self.pass_inp.text = ""
            print("خطأ: اسم المستخدم أو كلمة المرور غير صحيحة")

class OladMasrApp(App):
    def build(self):
        # 1. كود تسجيل الخطوط مع التأكد من وجود قيمة افتراضية
        potential_paths = [
            "/system/fonts/NotoNaskhArabic-Regular.ttf",
            "/system/fonts/DroidSansArabic.ttf",
            "/system/fonts/Roboto-Regular.ttf" 
        ]
        
        found_font = "Roboto" # قيمة افتراضية
        for path in potential_paths:
            if os.path.exists(path):
                found_font = path
                break
        
        # تسجيل الخط باسم AndroidArabic ليستخدمه التطبيق في كل مكان
        LabelBase.register(name="AndroidArabic", fn_regular=found_font)

        # 2. بناء الواجهات
        self.sm = ScreenManager()
        self.sm.add_widget(OrderFormScreen(name='form'))
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(InvoiceScreen(name='invoice'))
        
        # 3. تحميل البيانات وتفعيل التحديث التلقائي
        load_data(self) 
        
        # تشغيل فحص التحديثات من الإنترنت كل 5 دقائق (300 ثانية)
        Clock.schedule_interval(self.check_for_updates_periodically, 300)
        
        return self.sm

    def check_for_updates_periodically(self, dt):
        """فحص التحديثات في الخلفية تلقائياً"""
        def on_success(req, result):
            try:
                new_data = json.loads(result)
                app_data.update(new_data)
                save_data(app_data)
                self.refresh_ui()
                print("تم جلب بيانات محدثة من السيرفر بنجاح.")
            except Exception as e:
                print(f"خطأ في معالجة البيانات المجلوبة: {e}")

        # محاولة الاتصال بالسيرفر
        try:
            UrlRequest(SCRIPT_URL, on_success=on_success, on_error=lambda req, err: print("لا يوجد اتصال بالإنترنت حالياً."))
        except Exception:
            pass

    def refresh_ui(self):
        # تحديث شاشة الفورم
        if self.sm.has_screen('form'):
            form_screen = self.sm.get_screen('form')
            companies = form_screen.get_active_companies()
            if companies:
                form_screen.company_spinner.values = [fix_and_reshape_arabic(c) for c in companies]
                # لا نغير النص الافتراضي للـ spinner حتى لا نزعج المستخدم أثناء الكتابة
        
        # تحديث شاشة الإعدادات
        if self.sm.has_screen('settings'):
            self.sm.get_screen('settings').build_company_list()

        self.sm.get_screen('settings').build_company_list()

if __name__ == '__main__':
    OladMasrApp().run()
