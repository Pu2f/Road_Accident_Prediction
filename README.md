# Road Accident Prediction Dashboard

Dashboard สำหรับวิเคราะห์อุบัติเหตุทางถนน และคาดการณ์จำนวนผู้บาดเจ็บ

## Requirements

- Python 3.10 หรือ 3.11
- ติดตั้งแพ็กเกจด้วย `requirements.txt`

## Quick Start

```bash
pip install -r requirements.txt
python -m src.data.run_preprocess
python -m src.model.train_pycaret
python -m src.app.app
```

เปิดเว็บที่ `http://127.0.0.1:8050`

## Features

- `Overview`: ภาพรวมข้อมูลและกราฟสำคัญ
- `Forecast`: คาดการณ์จำนวนผู้บาดเจ็บ
- `Risk Map`: แผนที่ระดับความเสี่ยง