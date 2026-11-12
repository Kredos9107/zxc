import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'packages'))
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from pypdf import PdfReader
import fitz

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/pdf/module_measurements.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialBold', 'C:/Windows/Fonts/arialbd.ttf'))
c = canvas.Canvas(str(OUT), pagesize=(842,595))
c.setTitle('Размеры модулей для платы Vortex')
navy = HexColor('#18344B')
blue = HexColor('#236899')
def text(x,y,s,size=11,bold=False):
    c.setFillColor(navy); c.setFont('ArialBold' if bold else 'Arial',size); c.drawString(x,y,s)
def field(name,x,y,w=62,h=22):
    c.acroForm.textfield(name=name,tooltip=name,x=x,y=y,width=w,height=h,
        borderWidth=0.7,borderColor=blue,fillColor=HexColor('#EFF7FC'),
        textColor=navy,fontName='Helvetica',fontSize=11,forceBorder=True)
def row(name,label,y,x=420,w=90):
    text(x,y+7,label); field(name,718,y,w)
def base(title,num):
    text(34,553,title,23,True)
    text(34,527,'Все размеры в мм. Поля голубого цвета можно заполнять в PDF.',11)
    text(34,30,'Vortex • Бланк замеров • 10.11.2026',9)
    text(770,30,f'{num} / 3',9)
def hole(x,y,label):
    c.setFillColor(white);c.setStrokeColor(navy);c.circle(x,y,6,fill=1,stroke=1)
    text(x+10,y-4,label,10,True)
def board(x,y,w,h):
    c.setFillColor(HexColor('#E6F0F6'));c.setStrokeColor(blue)
    c.rect(x,y,w,h,fill=1,stroke=1)

base('HW-517: размеры и отверстия',1)
text(34,500,'Условный вид сверху со стороны компонентов. Не в масштабе.',10)
board(85,140,200,320)
for x,y,l in [(124,427,'P1'),(124,378,'P2'),(230,427,'P3'),(230,378,'P4')]:hole(x,y,l)
for i,x in enumerate([125,160,195,230]):hole(x,214,f'S{i+1}')
hole(144,174,'J1a');hole(214,174,'J1b')
text(108,307,'КОМПОНЕНТЫ',13,True)
text(85,112,'(0, 0): левый нижний угол модуля',10)
text(34,82,'X - вправо от левого края, Y - вверх от нижнего края.',10)
text(34,63,'Измеряй до центра отверстия. Ненужные отверстия можно пропустить.',10)
row('hw_width','Ширина платы',470)
row('hw_length','Длина платы',440)
text(420,408,'Отверстие',11,True);text(542,408,'X',11,True);text(624,408,'Y',11,True);text(714,408,'Диаметр',11,True)
for i,l in enumerate(['P1','P2','P3','P4','S1','S2','S3','S4','J1a','J1b']):
    y=376-i*26;text(420,y+6,l,11,True)
    field('hw_'+l+'_x',530,y);field('hw_'+l+'_y',614,y);field('hw_'+l+'_d',714,y,94)
text(420,98,'В какое отверстие ставим ШИМ?',10);field('hw_pwm',718,91,90)
text(420,68,'В какое отверстие ставим GND?',10);field('hw_gnd',718,61,90)
c.showPage()

base('XL4015: посадка и свободное место',2)
text(34,499,'Вид сверху: подстроечный резистор сверху, вход слева, выход справа.',10)
board(74,300,300,150)
hole(94,430,'IN+');hole(94,320,'IN-');hole(332,430,'OUT+');hole(332,320,'OUT-')
text(162,378,'XL4015',20,True)
text(74,275,'(0, 0): левый нижний угол модуля',10)
text(34,249,'Положение отверстий задаём от двух краёв модуля.',11)
row('xl_width','Ширина платы',465)
row('xl_length','Длина платы',433)
text(420,395,'Отверстие',11,True);text(542,395,'X',11,True);text(624,395,'Y',11,True);text(714,395,'Диаметр',11,True)
for i,l in enumerate(['IN+','IN-','OUT+','OUT-']):
    y=361-i*32;text(420,y+6,l,11,True)
    field('xl_'+l+'_x',530,y);field('xl_'+l+'_y',614,y);field('xl_'+l+'_d',714,y,94)
row('xl_height','Высота модуля над основной платой',195)
row('xl_under','Зазор под модулем до основной платы',160)
row('jp_height','Высота джампера с колпачком',125)
text(34,211,'Текущая помеха',14,True)
text(34,186,'Одна ножка джампера мешает преобразователю.',11)
text(34,165,'Одна из проволочных перемычек находится под ним.',11)
text(34,124,'При переделке нужен доступ к джамперу и перемычкам.',11)
text(34,103,'Габарит модуля учитываем вместе с выступающими деталями.',11)
text(420,84,'Выступ деталей за край, если есть (мм):',10)
field('xl_overhang',420,51,388)
c.showPage()

base('Энкодеры и требования к переделке',3)
text(34,487,'Четыре замечания к текущей плате',16,True)
items=[
'1. HW-517: отверстия ШИМ и GND не совпадают с модулем.',
'2. Джампер одной ножкой мешает преобразователю XL4015.',
'3. Второй энкодер требует неудобного разворота или перекручивания проводов.',
'4. Проволочные перемычки расположены неудобно, одна под XL4015.'
]
for i,s in enumerate(items):text(34,457-i*27,s,12)
text(34,322,'Ограничения компоновки',16,True)
text(34,293,'Сохранить примерно ту же площадь. Критерии методички проверим после её получения.',11)
text(34,271,'На этом этапе собираем замеры. Размеры и распиновку по фотографиям не угадываем.',11)
text(34,227,'Энкодер: замеры для проверки ориентации',15,True)
for name,label,y in [('enc_width','Ширина модуля энкодера',192),('enc_length','Длина модуля энкодера',160),('enc_pitch','Шаг между центрами соседних контактов',128),('enc_edge','Отступ ряда контактов от края модуля',96)]:row(name,label,y,x=34)
text(420,216,'Порядок выводов по фото со стороны вала:',10)
text(420,194,'GND, +, SW, DT, CLK (слева направо)',11,True)
text(420,162,'Пометка для ориентации второго энкодера:',10)
field('enc_orientation',420,126,270)
text(420,96,'Например: вал наружу, провода без перекручивания.',9)
c.showPage();c.save()
r=PdfReader(str(OUT)); fields=r.get_fields(); widgets=sum(len(p.get('/Annots',[])) for p in r.pages)
assert len(r.pages)==3 and len(fields)==widgets
doc=fitz.open(str(OUT))
for i,page in enumerate(doc):page.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(str(Path(__file__).parent/f'page-{i+1}.png'))
print(str(OUT));print('Pages:',len(r.pages),'fields:',len(fields),'widgets:',widgets)
