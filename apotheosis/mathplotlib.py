import matplotlib.pyplot as plt

days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
days1 = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
apple_sales = [10, 15, 12, 8, 14, 18, 20]
pear_sales = [8, 12, 10, 6, 11, 16, 19]

fig, axs = plt.subplots(1, 2, figsize=(10, 5))

axs[0].bar(days, apple_sales, color='tab:orange')
axs[0].set_title('Продажа яблок')
axs[0].set_xlabel('День недели')
axs[0].set_ylabel('Количество яблок')

axs[1].bar(days1, pear_sales, color='tab:green')
axs[1].set_title('Продажа груш')
axs[1].set_xlabel('День недели')
axs[1].set_ylabel('Количество груш')

plt.tight_layout()
plt.show()