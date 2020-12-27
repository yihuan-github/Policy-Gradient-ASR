from model import train
from model import predict
from data import find_maxlen, preproc
import argparse


def main(args):
   if args.mode=='train':
      train(args.train_path, args.dev_path, args.aud_path, args.alphabet,
            args.model_path, args.maxlen, args.maxlent, args.num_epochs, args.batch_size, args.device)
   elif args.mode=='predict':
      predict(args.test_path, args.aud_path, args.alphabet, args.model_path, 
              args.batch_size, args.maxlen, args.maxlent, args.device)
   elif args.mode=='preproc':
      preproc(args.corpus_path)



if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument('--train_path', type=str, help='Path to train csv')
   parser.add_argument('--dev_path', type=str, help="Path to dev csv")
   parser.add_argument('--test_path', type=str, help='Path to test csv')
   parser.add_argument('--corpus_path', type=str, help='Directory where the corpus is stored')
   parser.add_argument('--model_path', type=str, help="Directory where model logs and checkpoints will be saved.")
   parser.add_argument('--aud_path', type=str, help='Path to audio files')
   parser.add_argument('--alphabet', type=str, help='Path to alphabet file in .txt format')
   parser.add_argument('--num_epochs', nargs='?', type=int, default=10, help="Number of epochs")
   parser.add_argument('--batch_size', nargs='?', type=int, default=32, help='Batch size')
   parser.add_argument('--maxlen', nargs='?', const=1083, type=int, default=1083, help='Maximum input lenght')
   parser.add_argument('--maxlent', nargs='?', const=1083, type=int, default=1083, help='Maximum length of transcription')
   parser.add_argument('--mode', type=str, help="Select mode: train, predict", required=True)
<<<<<<< HEAD
   parser.add_argument('--resume', type=str)
   parser.add_argument('--device', type=int, help="Cuda device id")
=======
   parser.add_argument('--device', type=int, help="GPU id")
>>>>>>> main
   args = parser.parse_args()
   main(args)