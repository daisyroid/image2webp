#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
image2webp.py

使用方法:
    python image2webp.py image1.jpg image2.png *.png anim.gif
    python image2webp.py "写真フォルダ/*.jpg"

・ .webp で終わっているファイルはスキップ
・ それ以外の画像をWebPに変換
・ アニメーションGIF / APNG にも対応（透過・アニメーションを保持）
・ 元ファイルと同じ場所に「元ファイル名.webp」で保存
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageSequence


def convert_to_webp(filepath: str) -> bool:
    """
    1つのファイルをWebPに変換
    成功したらTrue、失敗したらFalseを返す
    """
    path = Path(filepath)

    # 既にwebpならスキップ
    if path.suffix.lower() == '.webp':
        print(f"スキップ（既にwebp）: {path}")
        return True

    output_path = path.with_suffix('.webp')

    try:
        with Image.open(path) as im:
            # アニメーションかどうかを判定
            is_animated = getattr(im, "is_animated", False)

            if is_animated:
                # アニメーションGIF / APNG の場合
                frames = []
                durations = []
                loop = 0

                for frame in ImageSequence.Iterator(im):
                    frames.append(frame.convert("RGBA"))
                    # 各フレームの表示時間（ミリ秒）
                    durations.append(frame.info.get("duration", 100))

                # APNGや一部GIFにあるループ回数
                loop = im.info.get("loop", 0)

                frames[0].save(
                    output_path,
                    format="WEBP",
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=loop,
                    quality=90,           # 画質（0-100）
                    method=4,             # 圧縮レベル（0=最速〜6=最高圧縮）
                    lossless=False
                )
            else:
                # 通常の静止画
                # RGBA → RGB に変換する場合もあるが、ここでは透過を保持
                im = im.convert("RGBA")
                im.save(
                    output_path,
                    format="WEBP",
                    quality=90,
                    method=4,
                    lossless=False
                )

            print(f"変換完了: {path} → {output_path}")
            return True

    except Exception as e:
        print(f"エラー: {path} → {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("使い方: python image2webp.py ファイルまたはワイルドカード...")
        print("例:   python image2webp.py *.jpg *.png anim.gif")
        sys.exit(1)

    success_count = 0
    fail_count = 0
    skip_count = 0

    # コマンドライン引数を順に処理（シェルで展開されたパスが来る）
    for arg in sys.argv[1:]:
        path = Path(arg)

        if path.is_file():
            if convert_to_webp(path):
                success_count += 1
            else:
                fail_count += 1
        elif path.is_dir():
            print(f"ディレクトリはスキップ: {path}")
        else:
            # ワイルドカードがシェルで展開されなかった場合（稀）
            print(f"見つかりません: {arg}")
            fail_count += 1

    print("\n" + "="*50)
    print(f"完了！  成功: {success_count}  失敗: {fail_count}  スキップ: {skip_count}")
    print("="*50)


if __name__ == "__main__":
    main()
