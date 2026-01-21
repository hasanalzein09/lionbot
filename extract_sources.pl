#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use open ':std', ':encoding(UTF-8)';

sub parse_res_md {
  my ($path, $out_fh) = @_;

  print {$out_fh} "SOURCE: res.md\n";

  open(my $fh, '<:encoding(UTF-8)', $path) or die "Cannot open $path: $!";

  my $want_rest_name = 0;
  my $restaurant = '';
  my $cat_ar = '';
  my $cat_en = '';
  my $category = '';

  while (my $line = <$fh>) {
    if ($line =~ /restaurant\\_info|\"restaurant_info\"/) {
      $want_rest_name = 1;
    }

    if ($want_rest_name && $line =~ /\"name\"\s*:\s*\"([^\"]+)\"/) {
      $restaurant = $1;
      $category = '';
      $cat_ar = '';
      $cat_en = '';
      print {$out_fh} "\nRESTAURANT: $restaurant\n";
      $want_rest_name = 0;
    }

    if ($line =~ /\"category\\_ar\"\s*:\s*\"([^\"]+)\"/) {
      $cat_ar = $1;
    }

    if ($line =~ /\"category\\_en\"\s*:\s*\"([^\"]+)\"/) {
      $cat_en = $1;
      my $c = $cat_ar;
      $c .= " / $cat_en" if length($cat_en);
      if ($restaurant ne '') {
        print {$out_fh} "  CATEGORY: $c\n";
      }
    }

    if ($line =~ /\"([A-Za-z0-9_]+)\"\s*:\s*\[/) {
      my $k = $1;
      if ($k ne 'menu' && $k ne 'items' && $k ne 'restaurant_info' && $k ne 'restaurant\\_info') {
        $category = $k;
        print {$out_fh} "  CATEGORY: $category\n" if $restaurant ne '';
      }
    }

    if ($line =~ /\"item\\_ar\"\s*:\s*\"([^\"]+)\".*?\"price\\_lbp\"\s*:\s*(\d+).*?\"price\\_usd\"\s*:\s*([0-9.]+)/) {
      print {$out_fh} "    - $1 | LBP $2 | USD $3\n";
      next;
    }

    if ($line =~ /\"item\\_ar\"\s*:\s*\"([^\"]+)\".*?\"price\"\s*:\s*([0-9.]+).*?\"currency\"\s*:\s*\"([^\"]+)\"/) {
      print {$out_fh} "    - $1 | $2 $3\n";
      next;
    }

    if ($line =~ /\"item\"\s*:\s*\"([^\"]+)\".*?\"price\"\s*:\s*([0-9.]+)/) {
      print {$out_fh} "    - $1 | $2\n";
      next;
    }
  }

  close($fh);
  print {$out_fh} "\n";
}

sub parse_rest2_md {
  my ($path, $out_fh) = @_;

  print {$out_fh} "SOURCE: rest2.md\n";

  open(my $fh, '<:encoding(UTF-8)', $path) or die "Cannot open $path: $!";

  my $in_rest = 0;
  my $rest_en = '';
  my $rest_ar = '';
  my $currency = '';
  my $printed_rest = 0;

  my $category = '';
  my $item_en = '';
  my $item_ar = '';

  while (my $line = <$fh>) {
    $line =~ tr/“”/"/;

    if ($line =~ /\"restaurant_info\"\s*:/) {
      $in_rest = 1;
      $printed_rest = 0;
      $rest_en = '';
      $rest_ar = '';
      $currency = '';
      next;
    }

    if ($in_rest) {
      $rest_en = $1 if $line =~ /\"name_en\"\s*:\s*\"([^\"]+)\"/;
      $rest_ar = $1 if $line =~ /\"name_ar\"\s*:\s*\"([^\"]+)\"/;
      $currency = $1 if $line =~ /\"currency\"\s*:\s*\"([^\"]+)\"/;

      if (!$printed_rest && (length($rest_en) || length($rest_ar))) {
        print {$out_fh} "\nRESTAURANT: $rest_en";
        print {$out_fh} " ($rest_ar)" if length($rest_ar);
        print {$out_fh} " | currency: $currency" if length($currency);
        print {$out_fh} "\n";
        $printed_rest = 1;
      }
    }

    if ($line =~ /\"category\"\s*:\s*\"([^\"]+)\"/) {
      $category = $1;
      print {$out_fh} "  CATEGORY: $category\n";
      next;
    }

    $item_en = $1 if $line =~ /\"name_en\"\s*:\s*\"([^\"]+)\"/;
    $item_ar = $1 if $line =~ /\"name_ar\"\s*:\s*\"([^\"]+)\"/;

    if ($line =~ /\"price\"\s*:\s*\"([^\"]+)\"/) {
      my $p = $1;
      if (length($item_en) || length($item_ar)) {
        print {$out_fh} "    - $item_en";
        print {$out_fh} " | $item_ar" if length($item_ar);
        print {$out_fh} " | $p\n";
      }
      $item_en = '';
      $item_ar = '';
      next;
    }
  }

  close($fh);
  print {$out_fh} "\n";
}

sub parse_doc4 {
  my ($path, $out_fh) = @_;

  print {$out_fh} "SOURCE: Document (4).docx\n";

  open(my $fh, '-|:encoding(UTF-8)', 'textutil', '-convert', 'txt', '-stdout', $path)
    or die "Failed to run textutil on $path: $!";

  local $/;
  my $text = <$fh>;
  $text =~ s/(\d)\s*\n\s*(\d)/$1$2/g;

  my $name_en = '';
  my $name_ar = '';
  my $printed = 0;

  my $cat_ar = '';
  my $cat_en = '';

  my $item = '';
  my $price = '';
  my $cur = '';

  for my $line (split(/\n/, $text)) {
    $name_en = $1 if $line =~ /\"name_en\"\s*:\s*\"([^\"]+)\"/;
    $name_ar = $1 if $line =~ /\"name_ar\"\s*:\s*\"([^\"]+)\"/;

    if (!$printed && (length($name_en) || length($name_ar))) {
      print {$out_fh} "\nRESTAURANT: $name_en";
      print {$out_fh} " ($name_ar)" if length($name_ar);
      print {$out_fh} "\n";
      $printed = 1;
    }

    $cat_ar = $1 if $line =~ /\"category_ar\"\s*:\s*\"([^\"]+)\"/;
    if ($line =~ /\"category_en\"\s*:\s*\"([^\"]+)\"/) {
      $cat_en = $1;
      my $c = $cat_ar;
      $c .= " / $cat_en" if length($cat_en);
      print {$out_fh} "  CATEGORY: $c\n";
    }

    $item = $1 if $line =~ /\"item_ar\"\s*:\s*\"([^\"]+)\"/;
    $price = $1 if $line =~ /\"price\"\s*:\s*([0-9.]+)/;
    $cur = $1 if $line =~ /\"currency\"\s*:\s*\"([^\"]+)\"/;

    if (length($item) && length($price) && length($cur)) {
      print {$out_fh} "    - $item | $price $cur\n";
      $item = '';
      $price = '';
      $cur = '';
    }
  }

  close($fh);
  print {$out_fh} "\n";
}

sub parse_doc7 {
  my ($path, $out_fh) = @_;

  print {$out_fh} "SOURCE: Document (7).docx\n";

  open(my $fh, '-|:encoding(UTF-8)', 'textutil', '-convert', 'txt', '-stdout', $path)
    or die "Failed to run textutil on $path: $!";

  local $/;
  my $text = <$fh>;
  $text =~ s/(\d)\s*\n\s*(\d)/$1$2/g;

  my $name_en = '';
  my $name_ar = '';
  my $printed = 0;

  my $category = '';
  my $item_en = '';
  my $item_ar = '';

  for my $line (split(/\n/, $text)) {
    $name_en = $1 if $line =~ /\"name_en\"\s*:\s*\"([^\"]+)\"/;
    $name_ar = $1 if $line =~ /\"name_ar\"\s*:\s*\"([^\"]+)\"/;

    if (!$printed && (length($name_en) || length($name_ar))) {
      print {$out_fh} "\nRESTAURANT: $name_en";
      print {$out_fh} " ($name_ar)" if length($name_ar);
      print {$out_fh} "\n";
      $printed = 1;
    }

    if ($line =~ /\"category_name\"\s*:\s*\"([^\"]+)\"/) {
      $category = $1;
      print {$out_fh} "  CATEGORY: $category\n";
      next;
    }

    $item_en = $1 if $line =~ /\"name_en\"\s*:\s*\"([^\"]+)\"/;
    $item_ar = $1 if $line =~ /\"name_ar\"\s*:\s*\"([^\"]+)\"/;

    if ($line =~ /\"price\"\s*:\s*([0-9.]+)/) {
      my $p = $1;
      if (length($item_en) || length($item_ar)) {
        print {$out_fh} "    - $item_en";
        print {$out_fh} " | $item_ar" if length($item_ar);
        print {$out_fh} " | $p\n";
      }
      $item_en = '';
      $item_ar = '';
      next;
    }
  }

  close($fh);
  print {$out_fh} "\n";
}

sub main {
  my $out_path = 'SOURCES_EXTRACTED.txt';
  open(my $out_fh, '>:encoding(UTF-8)', $out_path) or die "Cannot write $out_path: $!";

  parse_res_md('res.md', $out_fh);
  parse_rest2_md('admin_app/rest2.md', $out_fh);
  parse_doc4('Document (4).docx', $out_fh);
  parse_doc7('Document (7).docx', $out_fh);

  close($out_fh);
  print "Wrote $out_path\n";
}

main();
