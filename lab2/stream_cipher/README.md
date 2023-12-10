### How to use

1. Load files __Encoder\.py__, __Decoder\.py__ and __crypto_key.txt__. crypto_key.txt contains parameters of [linear congruent generator](https://ru.wikipedia.org/wiki/%D0%9B%D0%B8%D0%BD%D0%B5%D0%B9%D0%BD%D1%8B%D0%B9_%D0%BA%D0%BE%D0%BD%D0%B3%D1%80%D1%83%D1%8D%D0%BD%D1%82%D0%BD%D1%8B%D0%B9_%D0%BC%D0%B5%D1%82%D0%BE%D0%B4):
__X0, m, a, c__  
2. run Encoder\.py:

```bash
python Encoder.py <input_file_name> <output_file_name> <crypto_key_file_name>
```

3. run Decoder\.py:
```bash
python Decoder.py <input_file_name> <crypto_key_file_name>
```
