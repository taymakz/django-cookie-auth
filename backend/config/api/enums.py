from enum import Enum


class ResponseMessage(Enum):
    # Result Messages
    TIME_OUT = "خطای اتصال"
    SUCCESS = "عملیات با موفقیت انجام شد"
    FAILED = "خطایی در انجام عملیات رخ داده است"
    ACCESS_DENIED = "شما اجازه دسترسی ندارید"
    WRONG_PASSWORD = "کلمه عبور اشتباه میباشد"

    # Authentication / User
    LOGIN_REQUIRED = "برای ادامه، وارد شوید"
    AUTH_LOGIN_SUCCESSFULLY = "با موفقیت وارد شدید"
    AUTH_LOGOUT_SUCCESSFULLY = "با موفقیت خارج شدید"
    AUTH_WRONG_PASSWORD = "کلمه عبور اشتباه است"
    AUTH_WRONG_OTP = "کد تایید اشتباه یا منقضی شده است"
    NOT_VALID_PHONE = "شماره تلفن نامعتبر است"
    PHONE_OTP_SENT = "کد تایید به شماره {phone} ارسال شد"

    # Validation
    INVALID_INPUT = "ورودی نامعتبر است"
    REQUIRED_FIELD = "پر کردن این فیلد الزامی است"
    PASSWORDS_DO_NOT_MATCH = "رمز عبور و تکرار آن یکسان نیستند"

    # Database / Server
    NOT_FOUND = "موردی یافت نشد"
    DUPLICATE_ENTRY = "این مورد قبلاً ثبت شده است"
    INTERNAL_SERVER_ERROR = "خطای داخلی سرور"
    SERVICE_UNAVAILABLE = "سرویس در دسترس نیست"

    # File Handling
    FILE_TOO_LARGE = "فایل انتخاب‌شده بیش‌ازحد بزرگ است"
    UNSUPPORTED_FILE_TYPE = "نوع فایل پشتیبانی نمی‌شود"

    # Operation Specific
    ACTION_NOT_ALLOWED = "اجازه انجام این عملیات را ندارید"
    ALREADY_DONE = "این عملیات قبلاً انجام شده است"
    OPERATION_CANCELLED = "عملیات لغو شد"
