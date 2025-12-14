
if __name__ == "__main__":
    try:
        import insighter   # запускает твою основную программу
    except SystemExit:
        print(end='')
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
    finally:
        input("\nНажмите Enter, чтобы закрыть окно...")

